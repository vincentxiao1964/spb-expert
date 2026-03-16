from django.db.models import Q
from .models import CargoRequest, MatchResult
from market.models import ShipListing
import logging

logger = logging.getLogger(__name__)

class MatchingService:
    @staticmethod
    def match_cargo(cargo_request_id):
        try:
            cargo = CargoRequest.objects.get(id=cargo_request_id)
        except CargoRequest.DoesNotExist:
            logger.error(f"CargoRequest {cargo_request_id} not found")
            return []

        # 1. Basic Filtering
        # Find ships that are for charter (offer) and approved
        candidates = ShipListing.objects.filter(
            listing_type=ShipListing.ListingType.CHARTER_OFFER,
            status=ShipListing.Status.APPROVED
        )

        # Create match results
        matches = []
        for ship in candidates:
            score = MatchingService._calculate_score(cargo, ship)
            if score > 0:
                match, created = MatchResult.objects.get_or_create(
                    cargo_request=cargo,
                    ship_listing=ship,
                    defaults={'score': score}
                )
                if not created:
                    match.score = score
                    match.is_deleted = False  # Revive if re-matched
                    match.save()
                
                if not match.is_deleted:
                    matches.append(match)
        
        # Sort by score desc
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return matches

    @staticmethod
    def _calculate_score(cargo, ship):
        score = 0.0
        
        # Access extended info if available
        extended_info = None
        try:
            extended_info = ship.extended_info
        except Exception:
            extended_info = None

        # 1. Capacity Check (Hard Constraint + Precision)
        try:
            ship_dwt = float(ship.dwt) if ship.dwt else 0
        except ValueError:
            ship_dwt = 0
            
        if ship_dwt < cargo.weight:
            return 0.0
        dwt_tol_percent = cargo.dwt_tolerance_percent if getattr(cargo, 'dwt_tolerance_percent', None) is not None else 10.0
        if dwt_tol_percent < 0:
            dwt_tol_percent = 0.0
        dwt_tol_ratio = dwt_tol_percent / 100.0
        if (ship_dwt - cargo.weight) > (dwt_tol_ratio * cargo.weight):
             return 0.0

        # Capacity Score (0-0.3): Closer match is better
        # If ship is 2x larger, score drops.
        ratio = cargo.weight / ship_dwt
        # score += ratio * 0.3  <-- REMOVED accumulator logic
        
        # 1.1 Volume Check (if applicable)
        if cargo.volume and extended_info:
            ship_vol = extended_info.grain_capacity or extended_info.bale_capacity
            if ship_vol and ship_vol < cargo.volume:
                 return 0.0 # Volume too small
            
            if ship_vol:
                vol_ratio = cargo.volume / ship_vol
                # score += vol_ratio * 0.1 <-- REMOVED accumulator logic
        
        # 1.2 Draft Check (Hard Constraint + Precision)
        if cargo.max_draft and extended_info:
            ship_draft = extended_info.draft_laden or 0.0
            
            if ship_draft > cargo.max_draft:
                return 0.0
            draft_tol_percent = cargo.draft_tolerance_percent if getattr(cargo, 'draft_tolerance_percent', None) is not None else 10.0
            if draft_tol_percent < 0:
                draft_tol_percent = 0.0
            draft_tol_ratio = draft_tol_percent / 100.0
            if (cargo.max_draft - ship_draft) > (draft_tol_ratio * cargo.max_draft):
                 return 0.0
        
        # 2. Only Match Tonnage and Draft (No Route/Date)
        # Normalize score to 0.0 - 1.0 range based on capacity match
        # If ratio is 1.0 (perfect match), score is high.
        
        # Previous logic: score += ratio * 0.3 + vol_ratio * 0.1 + route * 0.3
        # New logic: score = ratio (weight/dwt)
        
        # We can just use the ratio directly as the base score.
        # Ideally, we want 100% if weight == dwt.
        # But usually cargo is smaller than DWT. 
        # Let's say: 
        # Score = (Cargo Weight / Ship DWT) * 0.8 + (Volume Match if applicable) * 0.2
        
        final_score = ratio * 0.8
        
        if cargo.volume and extended_info and extended_info.grain_capacity:
             vol_ratio = cargo.volume / extended_info.grain_capacity
             final_score += vol_ratio * 0.2
        else:
             # Distribute the remaining 0.2 to weight if no volume
             final_score = ratio * 1.0

        return min(final_score, 1.0)
        
        # 3. Date Match (0-0.3)
        # If ship is available before loading date
        if ship.start_time and ship.start_time <= cargo.loading_date:
            score += 0.3
        elif not ship.start_time:
            # If no start time specified, assume available (penalty)
            score += 0.1
            
        return round(score, 2)

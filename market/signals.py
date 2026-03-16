from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from .models import ShipListing, ListingMatch
import logging

logger = logging.getLogger(__name__)

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

@receiver(post_save, sender=ShipListing)
def trigger_matching(sender, instance, created, **kwargs):
    """
    Trigger matching logic when a listing is created or updated.
    Only proceed if status is APPROVED.
    """
    if instance.status == ShipListing.Status.APPROVED:
        find_matches(instance)

def find_matches(listing):
    """
    Find matches for the given listing based on:
    1. Category (Exact match)
    2. Type (Cross match: SELL <-> BUY, CHARTER_OFFER <-> CHARTER_REQUEST)
    3. Width (Difference < 2m)
    4. DWT (Difference < 1000t)
    """
    # Determine target type
    target_type = None
    if listing.listing_type == ShipListing.ListingType.SELL:
        target_type = ShipListing.ListingType.BUY
    elif listing.listing_type == ShipListing.ListingType.BUY:
        target_type = ShipListing.ListingType.SELL
    elif listing.listing_type == ShipListing.ListingType.CHARTER_OFFER:
        target_type = ShipListing.ListingType.CHARTER_REQUEST
    elif listing.listing_type == ShipListing.ListingType.CHARTER_REQUEST:
        target_type = ShipListing.ListingType.CHARTER_OFFER
    
    # If not SELL/BUY/CHARTER, we skip
    if not target_type:
        return

    # Base query: Category + Type + Approved + Not Own
    candidates = ShipListing.objects.filter(
        status=ShipListing.Status.APPROVED,
        listing_type=target_type,
        ship_category=listing.ship_category
    ).exclude(user=listing.user)

    # Get listing numerical values
    listing_dwt = safe_float(listing.dwt)
    listing_width = safe_float(listing.width)

    # Create Match Records
    new_matches_count = 0
    
    for candidate in candidates:
        is_match = True
        
        # Check DWT (Difference < 1000)
        if listing_dwt is not None:
            cand_dwt = safe_float(candidate.dwt)
            if cand_dwt is not None:
                if abs(listing_dwt - cand_dwt) >= 1000:
                    is_match = False
            else:
                # If candidate has no DWT, maybe strictly require it?
                # User said "Difference < 1000", implying both must exist.
                # Let's be strict: if DWT is missing, we can't verify difference.
                is_match = False 
        
        # Check Width (Difference < 2)
        if is_match and listing_width is not None:
            cand_width = safe_float(candidate.width)
            if cand_width is not None:
                if abs(listing_width - cand_width) >= 2:
                    is_match = False
            else:
                is_match = False
        
        if is_match:
            # Create match for the current listing (Source = Listing, Target = Candidate)
            match_obj, created = ListingMatch.objects.get_or_create(
                listing_source=listing,
                listing_target=candidate,
                defaults={'score': 1.0}
            )
            if created:
                new_matches_count += 1
                
            # Create reciprocal match (Source = Candidate, Target = Listing)
            ListingMatch.objects.get_or_create(
                listing_source=candidate,
                listing_target=listing,
                defaults={'score': 1.0}
            )

    if new_matches_count > 0:
        logger.info(f"Created {new_matches_count} matches for listing {listing.id}")

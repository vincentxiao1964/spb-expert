/**
 * Social Actions (Follow & Favorite)
 * Shared logic for handling follow/unfollow and favorite/unfavorite actions.
 * Supports multiple buttons per page.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Helper to get cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // --- Follow Functionality ---
    const followButtons = document.querySelectorAll('.btn-follow');
    followButtons.forEach(btnFollow => {
        const userId = btnFollow.dataset.userId;
        if (!userId) return;

        // Initial Check
        fetch(`/api/v1/following/check/?followed_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                updateFollowButton(btnFollow, data.is_following);
            })
            .catch(err => console.error('Error checking follow status:', err));
            
        // Toggle Action
        btnFollow.addEventListener('click', function() {
            fetch('/api/v1/following/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ followed_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                updateFollowButton(btnFollow, data.is_following);
            })
            .catch(err => console.error('Error toggling follow:', err));
        });
    });

    function updateFollowButton(btn, isFollowing) {
        if (isFollowing) {
            btn.innerHTML = '<i class="fas fa-user-minus"></i> Unfollow'; 
            btn.classList.replace('btn-outline-primary', 'btn-primary');
            // Use data-text if available for translations
            if (btn.dataset.textUnfollow) btn.innerHTML = `<i class="fas fa-user-minus"></i> ${btn.dataset.textUnfollow}`;
            if (btn.title) btn.title = btn.dataset.textUnfollow || 'Unfollow';
        } else {
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Follow User';
            btn.classList.replace('btn-primary', 'btn-outline-primary');
            if (btn.dataset.textFollow) btn.innerHTML = `<i class="fas fa-user-plus"></i> ${btn.dataset.textFollow}`;
            if (btn.title) btn.title = btn.dataset.textFollow || 'Follow User';
        }
    }

    // --- Favorite Functionality ---
    const favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(btnFavorite => {
        const objectId = btnFavorite.dataset.objectId;
        const contentType = btnFavorite.dataset.contentType;
        if (!objectId || !contentType) return;

        // Initial Check
        fetch(`/api/v1/favorites/check/?object_id=${objectId}&content_type=${contentType}`)
            .then(response => response.json())
            .then(data => {
                updateFavoriteButton(btnFavorite, data.is_favorite);
            })
            .catch(err => console.error('Error checking favorite status:', err));
            
        // Toggle Action
        btnFavorite.addEventListener('click', function() {
            fetch('/api/v1/favorites/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ object_id: objectId, content_type: contentType })
            })
            .then(response => response.json())
            .then(data => {
                updateFavoriteButton(btnFavorite, data.is_favorite);
            })
            .catch(err => console.error('Error toggling favorite:', err));
        });
    });

    function updateFavoriteButton(btn, isFavorite) {
        if (isFavorite) {
            btn.innerHTML = '<i class="fas fa-star"></i> Favorite';
            btn.classList.replace('btn-outline-warning', 'btn-warning');
            if (btn.dataset.textUnfavorite) btn.innerHTML = `<i class="fas fa-star"></i> ${btn.dataset.textUnfavorite}`;
            else if (btn.dataset.textFavorite) btn.innerHTML = `<i class="fas fa-star"></i> ${btn.dataset.textFavorite}`; // Fallback if unfavorite text not set
            
            // Handle icon-only buttons (if they have specific styling or no text initially)
            // If the button had no text initially (just icon), we might want to keep it that way?
            // But here we enforce text if data-text is present. 
            // For list views with icon only, we should handle that.
            
            // Check if it's an icon-only button (simple heuristic: if innerHTML was very short or just <i>)
            // Better approach: User data-icon-only="true"
            if (btn.dataset.iconOnly === 'true') {
                 btn.innerHTML = `<i class="fas fa-star"></i>`;
            }
            
            if (btn.title) btn.title = btn.dataset.textUnfavorite || 'Unfavorite';
            
        } else {
            btn.innerHTML = '<i class="fas fa-star"></i> Favorite';
            btn.classList.replace('btn-warning', 'btn-outline-warning');
            if (btn.dataset.textFavorite) btn.innerHTML = `<i class="fas fa-star"></i> ${btn.dataset.textFavorite}`;
            
            if (btn.dataset.iconOnly === 'true') {
                 btn.innerHTML = `<i class="fas fa-star"></i>`;
            }

            if (btn.title) btn.title = btn.dataset.textFavorite || 'Favorite';
        }
    }
});

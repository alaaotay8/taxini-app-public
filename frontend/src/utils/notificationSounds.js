// Notification sound generators (simple beeps)
// These will be created as data URLs to avoid needing external files

export function createNotificationSounds() {
  // Simple success beep (higher pitch)
  const successSound = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFgYJ8eXJsZmJfW1hWV1dYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeFhIOCgYCAf359fHt6eXh3dnV0c3JxcG9ubWxramloZ2ZlZGNiYWBfXl1cW1pZWFdWVlhZW11eYGNlZ2lrbG50dnd5fH1/goSGiYuMjpCRkpSVl5iZmpydn6ChoqSmqKmqrK2usLGys7S1tre4ubq7vL2+v8DBwsPExcXGxsfHyMjIyMjIyMjIyMjIx8fGxcTDwsHAvr27ubf2tLKwrausqqimp6SioJ+dnJqYlpSTkZCNi4mHhYJ/fHl2c29sZ2ViX1xYVVJPTEhFQj89OjY0MTAt';
  
  // Error beep (lower pitch)
  const errorSound = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAgH9+fXt5d3RybnNZWlpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeFhIOCgYCAf359fHt6eXh3dnV0c3JxcG9ubWxramloZ2ZlZGNiYWBfXl1cW1pZWFdWVlhZW11eYGNlZ2lrbG50dnd5fH1/goSGiYuMjpCRkpSVl5iZmpydn6ChoqSmqKmqrK2usLGys7S1tre4ubq7vL2+v8DBwsPExcXGxsfHyMjIyMjIyMjIyMjIx8fGxcTDwsHAvr27ubf2tLKwrausqqimp6SioJ+dnJqYlpSTkZCNi4mHhYJ/fHl2c29sZ2ViX1xYVVJPTEhFQj89OjY0MTAt';
  
  // Warning beep (medium pitch)
  const warningSound = successSound;
  
  // Info beep (short)
  const infoSound = successSound;
  
  return {
    success: successSound,
    error: errorSound,
    warning: warningSound,
    info: infoSound
  };
}

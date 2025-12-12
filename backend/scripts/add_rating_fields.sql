-- Add rating comment and completion confirmation fields to trips table
-- Run this on Supabase SQL editor or via psql

ALTER TABLE trips 
ADD COLUMN IF NOT EXISTS rider_rating_comment VARCHAR(500),
ADD COLUMN IF NOT EXISTS driver_rating_comment VARCHAR(500),
ADD COLUMN IF NOT EXISTS rider_confirmed_completion BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS rider_confirmed_completion_at TIMESTAMP;

-- Verify columns were added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'trips' 
AND column_name IN ('rider_rating_comment', 'driver_rating_comment', 'rider_confirmed_completion', 'rider_confirmed_completion_at')
ORDER BY column_name;

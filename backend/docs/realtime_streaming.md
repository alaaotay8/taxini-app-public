# Real-time GPS Streaming Documentation

This document explains how the real-time GPS streaming system works in the Taxini application, covering backend APIs, Supabase WebSocket integration, and frontend connection steps.

## System Overview

The real-time GPS streaming system allows drivers' GPS coordinates to be broadcast in real-time to client applications using WebSockets. The system follows this flow:

1. **Backend API**: Exposes endpoints to start/stop streaming for a driver
2. **Supabase Realtime**: Handles WebSocket connections and broadcasting
3. **Frontend Client**: Connects to the specific driver's channel to receive updates

## Backend API

### Start Streaming

**Endpoint**: `POST /api/v1/users/driver/streaming/start`

**Request**:
```json
{
  "driver_id": "user-uuid-here"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Real-time streaming started",
  "driver_id": "user-uuid-here",
  "channel": "driver_user-uuid-here"
}
```

The `channel` field in the response tells the frontend which channel to subscribe to for receiving GPS updates.

### Stop Streaming

**Endpoint**: `POST /api/v1/users/driver/streaming/stop`

**Request**:
```json
{
  "driver_id": "user-uuid-here"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Real-time streaming stopped",
  "driver_id": "user-uuid-here",
  "updates_sent": 42
}
```

## Backend Implementation Details

The backend implementation uses the `RealtimeLocationService` class in `src/services/realtime_location.py`. This service:

1. Creates a driver-specific channel name (`driver_[id]`)
2. Connects to Supabase Realtime WebSocket server
3. Streams GPS coordinates from a predefined route in 5-second intervals
4. Broadcasts updates to the driver-specific channel
5. Handles cleanup on stream termination

Key code snippet for channel creation:
```python
# Create channel with broadcast config - use driver-specific channel
channel_name = f"driver_{driver_id}"
channel = client.channel(channel_name, {"config": {"broadcast": {"ack": False, "self": False}}})
```

Broadcasting GPS updates:
```python
await channel.send_broadcast("gps_update", gps_data)
```

## Supabase Realtime

Supabase Realtime provides the WebSocket infrastructure. The system uses pure WebSocket channels (not database tables) for maximum performance.

1. WebSocket URL: `wss://[project-ref].supabase.co/realtime/v1/websocket`
2. Authentication: Uses Supabase API key
3. Channel Configuration: `{"broadcast": {"ack": false, "self": false}}`
4. Event Type: `gps_update`

## Frontend Integration (React)

To integrate with a React frontend:

1. Install Supabase JS client:
   ```bash
   npm install @supabase/supabase-js
   ```

2. Initialize Supabase client:
   ```javascript
   import { createClient } from '@supabase/supabase-js';

   const supabaseUrl = 'https://your-project.supabase.co';
   const supabaseKey = 'your-anon-key';
   const supabase = createClient(supabaseUrl, supabaseKey);
   ```

3. Connect to driver-specific channel:
   ```javascript
   const connectToDriverChannel = async (driverId) => {
     try {
       // Start streaming via REST API
       const response = await fetch('/api/v1/users/driver/streaming/start', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({ driver_id: driverId }),
       });
       
       const data = await response.json();
       
       if (data.success && data.channel) {
         // Get channel name from response
         const channelName = data.channel;
         
         // Connect to the channel
         const channel = supabase
           .channel(channelName)
           .on('broadcast', { event: 'gps_update' }, (payload) => {
             // Handle GPS update
             console.log('GPS Update:', payload);
             
             // Update driver marker on map
             updateDriverLocation(payload.payload);
           })
           .subscribe((status) => {
             console.log('Subscription status:', status);
           });
           
         // Store channel reference for later cleanup
         return channel;
       }
     } catch (error) {
       console.error('Error connecting to driver channel:', error);
     }
   };
   ```

4. Disconnect and stop streaming:
   ```javascript
   const disconnectFromDriverChannel = async (channel, driverId) => {
     // Unsubscribe from channel
     if (channel) {
       await supabase.removeChannel(channel);
     }
     
     // Stop streaming via REST API
     try {
       await fetch('/api/v1/users/driver/streaming/stop', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({ driver_id: driverId }),
       });
     } catch (error) {
       console.error('Error stopping stream:', error);
     }
   };
   ```

5. Example React component for tracking a driver:
   ```jsx
   import React, { useEffect, useState } from 'react';
   import { createClient } from '@supabase/supabase-js';
   import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

   const supabase = createClient('https://your-project.supabase.co', 'your-anon-key');

   const DriverTracker = ({ driverId }) => {
     const [channel, setChannel] = useState(null);
     const [location, setLocation] = useState(null);
     
     // Connect to driver's channel on component mount
     useEffect(() => {
       const connectChannel = async () => {
         const newChannel = await connectToDriverChannel(driverId);
         setChannel(newChannel);
       };
       
       connectChannel();
       
       // Cleanup on component unmount
       return () => {
         if (channel) {
           disconnectFromDriverChannel(channel, driverId);
         }
       };
     }, [driverId]);
     
     // Function to connect to driver channel
     const connectToDriverChannel = async (id) => {
       try {
         const response = await fetch('/api/v1/users/driver/streaming/start', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ driver_id: id }),
         });
         
         const data = await response.json();
         
         if (data.success && data.channel) {
           const channelName = data.channel;
           
           const channel = supabase
             .channel(channelName)
             .on('broadcast', { event: 'gps_update' }, (payload) => {
               // Update location state with received coordinates
               setLocation({
                 lat: payload.payload.latitude,
                 lng: payload.payload.longitude,
                 timestamp: payload.payload.timestamp
               });
             })
             .subscribe();
             
           return channel;
         }
       } catch (error) {
         console.error('Error connecting to driver channel:', error);
       }
     };
     
     return (
       <div className="driver-tracker">
         <h2>Tracking Driver: {driverId}</h2>
         
         {location ? (
           <>
             <div>
               <p>Last update: {new Date(location.timestamp).toLocaleTimeString()}</p>
               <p>Coordinates: {location.lat}, {location.lng}</p>
             </div>
             
             <MapContainer center={[location.lat, location.lng]} zoom={15} style={{ height: '400px' }}>
               <TileLayer
                 url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                 attribution='&copy; OpenStreetMap contributors'
               />
               <Marker position={[location.lat, location.lng]}>
                 <Popup>Driver is here</Popup>
               </Marker>
             </MapContainer>
           </>
         ) : (
           <p>Waiting for driver location updates...</p>
         )}
       </div>
     );
   };

   export default DriverTracker;
   ```

## Payload Format

The GPS update payload has this structure:

```json
{
  "driver_id": "user-uuid-here",
  "latitude": 33.8978,
  "longitude": 35.5058,
  "timestamp": "2025-08-22T14:30:45.123Z",
  "step": 5,
  "total_steps": 39
}
```

## Security Considerations

1. The current implementation uses Supabase anon key for simplicity
2. For production, consider using row-level security and authenticated users
3. The test endpoints don't require authentication - secure these for production

## Performance Notes

1. Updates are sent every 5 seconds to balance responsiveness and bandwidth
2. WebSocket connections are more efficient than polling for real-time tracking
3. Each driver gets a dedicated channel for scalability



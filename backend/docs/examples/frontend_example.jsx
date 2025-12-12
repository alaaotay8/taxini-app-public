import React, { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Initialize Supabase client
const supabaseUrl = 'https://your-project-ref.supabase.co';
const supabaseKey = 'your-anon-key';
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * DriverTracker Component
 * 
 * This component demonstrates how to:
 * 1. Start GPS streaming for a driver via API
 * 2. Connect to the driver's specific WebSocket channel
 * 3. Receive and display real-time GPS updates
 * 4. Clean up connections when component unmounts
 */
const DriverTracker = ({ driverId }) => {
  const [channel, setChannel] = useState(null);
  const [location, setLocation] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [updates, setUpdates] = useState([]);

  // Connect to driver's channel on component mount
  useEffect(() => {
    let mounted = true;
    
    const connectChannel = async () => {
      try {
        // 1. Call API to start streaming
        const response = await fetch('/api/v1/users/driver/streaming/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ driver_id: driverId }),
        });
        
        const data = await response.json();
        console.log('API response:', data);
        
        if (!data.success || !data.channel) {
          throw new Error('Failed to start streaming or missing channel name');
        }
        
        // 2. Get channel name from response
        const channelName = data.channel;
        console.log(`Connecting to channel: ${channelName}`);
        
        // 3. Subscribe to the channel
        const newChannel = supabase
          .channel(channelName)
          .on('broadcast', { event: 'gps_update' }, (payload) => {
            // Handle received GPS update
            console.log('Received GPS update:', payload);
            
            if (mounted) {
              // Update current location
              const newLocation = {
                lat: payload.payload.latitude,
                lng: payload.payload.longitude,
                timestamp: payload.payload.timestamp,
                step: payload.payload.step,
                total: payload.payload.total_steps
              };
              
              setLocation(newLocation);
              
              // Add to history (limited to last 10 updates)
              setUpdates(prev => {
                const updated = [newLocation, ...prev];
                return updated.slice(0, 10);
              });
            }
          })
          .subscribe((status) => {
            console.log(`Subscription status: ${status}`);
            if (status === 'SUBSCRIBED' && mounted) {
              setIsConnected(true);
            }
          });
        
        if (mounted) {
          setChannel(newChannel);
        } else {
          // Clean up if component unmounted during async operation
          supabase.removeChannel(newChannel);
        }
      } catch (error) {
        console.error('Error connecting to driver channel:', error);
      }
    };
    
    connectChannel();
    
    // Cleanup on unmount
    return () => {
      mounted = false;
      disconnectFromDriverChannel();
    };
  }, [driverId]);
  
  // Disconnect and stop streaming
  const disconnectFromDriverChannel = async () => {
    try {
      // 1. Unsubscribe from channel
      if (channel) {
        await supabase.removeChannel(channel);
      }
      
      // 2. Call API to stop streaming
      await fetch('/api/v1/users/driver/streaming/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ driver_id: driverId }),
      });
      
      setChannel(null);
      setIsConnected(false);
    } catch (error) {
      console.error('Error disconnecting:', error);
    }
  };
  
  // For demonstration, allow manual reconnect
  const handleReconnect = () => {
    disconnectFromDriverChannel().then(() => {
      // Wait a moment and reconnect
      setTimeout(() => {
        connectChannel();
      }, 1000);
    });
  };

  return (
    <div className="driver-tracker">
      <h2>Driver GPS Tracker</h2>
      
      <div className="connection-status">
        <p>
          Status: <span className={isConnected ? 'status-connected' : 'status-disconnected'}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </p>
        <p>Driver ID: {driverId}</p>
        <p>Channel: {channel ? `driver_${driverId}` : 'Not connected'}</p>
      </div>
      
      {location ? (
        <div className="location-info">
          <h3>Current Location</h3>
          <p>Timestamp: {new Date(location.timestamp).toLocaleTimeString()}</p>
          <p>Coordinates: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}</p>
          <p>Step: {location.step} / {location.total}</p>
          
          {/* Map display */}
          <div className="map-container">
            <MapContainer 
              center={[location.lat, location.lng]} 
              zoom={15} 
              style={{ height: '400px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
              />
              <Marker position={[location.lat, location.lng]}>
                <Popup>Driver is here</Popup>
              </Marker>
            </MapContainer>
          </div>
          
          {/* Update history */}
          <div className="update-history">
            <h3>Recent Updates</h3>
            <ul>
              {updates.map((update, index) => (
                <li key={index}>
                  {new Date(update.timestamp).toLocaleTimeString()} - 
                  {update.lat.toFixed(4)}, {update.lng.toFixed(4)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="waiting-message">
          <p>Waiting for location updates...</p>
          {isConnected && <p>Connection established. GPS data should arrive soon.</p>}
        </div>
      )}
      
      <div className="controls">
        <button onClick={disconnectFromDriverChannel} disabled={!channel}>
          Stop Tracking
        </button>
        <button onClick={handleReconnect} disabled={!!channel}>
          Reconnect
        </button>
      </div>
      
      <style jsx>{`
        .driver-tracker {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .connection-status {
          margin-bottom: 20px;
          padding: 10px;
          background: #f5f5f5;
          border-radius: 4px;
        }
        
        .status-connected {
          color: green;
          font-weight: bold;
        }
        
        .status-disconnected {
          color: red;
          font-weight: bold;
        }
        
        .map-container {
          margin: 20px 0;
          border: 1px solid #ddd;
          border-radius: 4px;
          overflow: hidden;
        }
        
        .controls {
          margin-top: 20px;
        }
        
        button {
          margin-right: 10px;
          padding: 8px 16px;
        }
        
        .update-history {
          margin-top: 20px;
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #eee;
          padding: 10px;
        }
      `}</style>
    </div>
  );
};

export default DriverTracker;

// Example usage in a parent component:
/*
import DriverTracker from './DriverTracker';

function App() {
  const driverId = 'ea108ea3-97b3-44f7-aae8-4c9abc64824e';
  
  return (
    <div className="App">
      <header>
        <h1>Driver Tracking Demo</h1>
      </header>
      <main>
        <DriverTracker driverId={driverId} />
      </main>
    </div>
  );
}
*/

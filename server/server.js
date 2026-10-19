// Lightweight cache server for GTFS data
// Returns processed JSON for vehicles positions and updates (delays), protobuf GTFS for alerts

const express = require('express');
const cors = require('cors');
const GtfsRealtimeBindings = require('gtfs-realtime-bindings');
const fetch = require('node-fetch');
const app = express();
const PORT = process.env.PORT || 3000;
const utils = require('./utils.js')
const { loadEnvFile } = require('node:process');
loadEnvFile('.env');
console.log(process.env);

const CONFIG = {
    KK: process.env.KK,
    vehicleUrl: process.env.RT_VEHICLE_API_URL,
    alertUrl: process.env.RT_ALERT_API_URL,
    updateUrl: process.env.RT_UPDATE_API_URL,
    refreshInterval: process.env.RT_REFRESH_RATE || 10000,
    alertsRefreshInterval: 1 * 60 * 60 * 1000, // one alert request per hour
    apiKey: process.env.API_KEY || '',
    verboseLogging: process.env.VERBOSE_LOGGING === 'true' // by default false in prod
};

// Cache data into memory
let cachedData = {
    vehicles: null,
    alerts: null,
    alertsRaw: null, //gtfs protobuf
    updates: null,
    delayByTrip: {},
    lastUpdate: {
	vehicles: null,
	alerts: null,
	alertsRaw: null,
	updates: null
  }
};

// ----------------------------------------------------------------------------------
// Activate CORS to allow requests from front-end
app.use(cors());

// Serve and use utils.js as static file
app.use('/utils.js', express.static(__dirname + '/utils.js'));


// Conditional logging
function log(message, force = false) {
  if (CONFIG.verboseLogging || force) {
    console.log(message);
  }
}

// ----------------------------------------------------------------------------------
// Get and convert vehicles data from GTFS protobuf to JSON
async function fetchAndConvertVehicles() {
  try {
    log(`[${new Date().toISOString()}] Fetching vehicle data...`);
      //const headers = {};
      const headers = {"bmc-partner-key": CONFIG.KK};
      const response = await fetch(CONFIG.vehicleUrl, { headers });
      
      console.log(response);
      
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const buffer = await response.arrayBuffer();
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(
      new Uint8Array(buffer)
    );

    // Convert into usable JSON
    const formattedVehicleData = feed.entity.map(entity => {
      if (!entity.vehicle) return null;

      const vehicle = entity.vehicle;
	const position = vehicle.position;
	
      return {
          vehicleId: vehicle.vehicle?.id || entity.id,
	  latitude: position?.latitude || null,
          longitude: position?.longitude || null,
	  speed: position?.speed || null,
	  currentStopSequence: vehicle.currentStopSequence || null,
          //timestamp: vehicle.timestamp?.toNumber() || null,
	  stopId: vehicle.stopId || null,
	  trip: vehicle.trip? {
              tripId: vehicle.trip.tripId || null,
              routeId: vehicle.trip.routeId || null,
              //startTime: vehicle.trip.startTime || null,
              //startDate: vehicle.trip.startDate || null,
	      //route_short_name and route_long_name are computed in client who have static gtfs data
	      //route_short_name: utils.getRouteShortName(vehicle.trip.routeId) || null, // TO DO server-side
	      //route_long_name: utils.getRouteLongName(vehicle.trip.routeId) || null,   // TO DO server-side
	  } : null,
	  //agency: vehicle.trip?.routeId?.split("-")[0] || null // agendy id from route id
        //bearing: position?.bearing || null,
        //currentStatus: vehicle.currentStatus || null,
      };
    }).filter(v => v !== null);

    log(formattedVehicleData);
      
    cachedData.vehicles = formattedVehicleData;
    cachedData.lastUpdate.vehicles = new Date();
    
    log(`[${new Date().toISOString()}] Vehicle data updated: ${formattedVehicleData.length} vehicles`);
    
    return formattedVehicleData;
  } catch (error) {
    console.error('Error fetching vehicle data:', error.message);
    return null;
  }
}


// ----------------------------------------------------------------------------------
// Get and forward raw GTFS protobuf data for alerts (later processed client-side)
async function fetchAlertsRaw() {
    try {
	log(`[${new Date().toISOString()}] Fetching Alert data...`);
	//const headers = {};
	const headers = {"bmc-partner-key": CONFIG.KK};
	const response = await fetch(CONFIG.alertUrl, { headers });
      
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const buffer = await response.arrayBuffer();
    
    // Store raw buffer
    cachedData.alertsRaw = buffer;
    cachedData.lastUpdate.alertsRaw = new Date();
    
    log(`[${new Date().toISOString()}] Raw alerts data cached: ${buffer.byteLength} bytes`);
    
    return buffer;
  } catch (error) {
    console.error('Error fetching raw alerts data:', error.message);
    return null;
  }
}


// ----------------------------------------------------------------------------------
// Get and convert updates (delays) data from GTFS protobuf to JSON
async function fetchAndConvertUpdates() {
  try {
    log(`[${new Date().toISOString()}] Fetching trip updates data...`);
    
      //const headers = {};
      const headers = {"bmc-partner-key": CONFIG.KK};
    const response = await fetch(CONFIG.updateUrl, { headers });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const buffer = await response.arrayBuffer();
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(
      new Uint8Array(buffer)
    );

    // Convert into usable JSON
    const formattedUpdateData = [];
    const delayByTrip = {};

    feed.entity.forEach(entity => {
      if (!entity.tripUpdate) return;

      const tripUpdate = entity.tripUpdate;
      const tripId = tripUpdate.trip?.tripId;

      if (!tripId) return;

      // get delay for trip 
      const tripDelay = tripUpdate.delay || null;
      
      // store in data structure
      if (tripDelay !== null) {
        delayByTrip[tripId] = Math.round(tripDelay/60); // delay in minutes
      }
    });

    //cachedData.updates = formattedUpdateData;
    cachedData.delayByTrip = delayByTrip;
    cachedData.lastUpdate.updates = new Date();
    
    log(`[${new Date().toISOString()}] Trip updates data updated: ${formattedUpdateData.length} trips, ${Object.keys(delayByTrip).length} with delays`);
    
      //return { updates: formattedUpdateData, delayByTrip };
      return { updates: delayByTrip };
      
  } catch (error) {
    console.error('Error fetching trip updates data:', error.message);
    return null;
  }
}



// ----------------------------------------------------------------------------------
// Routes API

// api endpoint for vehicle positions in JSON
app.get('/api/vehicles', (req, res) => {
  if (!cachedData.vehicles) {
    return res.status(503).json({ 
      error: 'Data not yet available',
      message: 'Server is initializing, please retry in a few seconds'
    });
  }
  res.json({
    data: cachedData.vehicles,
    lastUpdate: cachedData.lastUpdate.vehicles,
    count: cachedData.vehicles.length
  });
});


// api endpoint for raw alerts in protobuf 
app.get('/api/alerts/raw', (req, res) => {
  if (!cachedData.alertsRaw) {
    return res.status(503).json({ 
      error: 'Data not yet available',
      message: 'Server is initializing, please retry in a few seconds'
    });
  }
  // headers for protobuf
  res.set({
    'Content-Type': 'application/x-protobuf',
    'Content-Length': cachedData.alertsRaw.byteLength
  });
  // sent raw buffer
  res.send(Buffer.from(cachedData.alertsRaw));
});


//api endpoint for alerts (json, lacks human-readable cancellation times)
app.get('/api/alerts', (req, res) => {
  if (!cachedData.alerts) {
    return res.status(503).json({ 
      error: 'Data not yet available',
      message: 'Server is initializing, please retry in a few seconds'
    });
  }
  res.json({
    data: cachedData.alerts,
    lastUpdate: cachedData.lastUpdate.alerts,
    count: cachedData.alerts.length
  });
});


// api endpoint to get delays for tripids (simplified format)
app.get('/api/delays', (req, res) => {
  if (!cachedData.delayByTrip) {
    return res.status(503).json({ 
      error: 'Data not yet available',
      message: 'Server is initializing, please retry in a few seconds'
    });
  }
  res.json({
    delayByTrip: cachedData.delayByTrip,
    lastUpdate: cachedData.lastUpdate.updates,
    count: Object.keys(cachedData.delayByTrip).length
  });
});


// Status endpoint to check server is running and last updates
app.get('/status', (req, res) => {
  res.json({
    status: 'okdoki_v2',
    uptime: process.uptime(),
    lastUpdate: cachedData.lastUpdate,
      dataAvailable: {
	  vehicles: cachedData.vehicles !== null,
	  alerts: cachedData.alerts !== null,
	  delays: cachedData.delayByTrip !== null
      }
  });
});


// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'GTFS Realtime Cache Server',
    endpoints: {
	vehicles: '/api/vehicles',
	alerts: '/api/alerts',
	alertsRaw: '/api/alerts/raw',	
	//updates: '/api/updates',
	delays: '/api/delays',
	health: '/status'
    }
  });
});


// ----------------------------------------------------------------------------------
// Init and start server
async function init() {
    log('GTFS Cache Server v2 starting...');
    log('Configuration:', {
      vehicleUrl: CONFIG.vehicleUrl,
      alertUrl: CONFIG.alertUrl,
      updateUrl: CONFIG.updateUrl,
      refreshInterval: CONFIG.refreshInterval,
      port: PORT
  });

    // Get first data when server starts
    await Promise.all([
	fetchAndConvertVehicles(),
	fetchAlertsRaw(),
	fetchAndConvertUpdates()
    ]);

  // Update data
    setInterval(fetchAndConvertVehicles, CONFIG.refreshInterval);
    setInterval(fetchAlertsRaw, CONFIG.alertsRefreshInterval);
    setInterval(fetchAndConvertUpdates, CONFIG.refreshInterval);

  // Start HTTP server
  app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Verbose logging: ${CONFIG.verboseLogging ? 'enabled' : 'disabled (set VERBOSE_LOGGING=true to enable)'}`);
      console.log(`Access it at http://localhost:${PORT}`);
  });
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Start
init();

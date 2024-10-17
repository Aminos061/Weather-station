import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;

class WeatherStation {
  final String location;
  final LatLng coordinates;
  final String address; // Address field
  final double? battery;
  final double? batteryVoltage;
  final String? gwid;
  final double? humidity0;
  final double? humidity4;
  final double? humidity;
  final double? light0;
  final double? rssirf;
  final double? rain0;
  final double? temperature0;
  final double? temperature4;
  final double? temperature;
  final String timestamp;
  final double? uv0;
  final double? winddirection0;
  final double? winddirection0Offset;
  final double? windspeedAvg0;
  final double? windspeedMax0;
  final int? bootCount;

  WeatherStation({
    required this.location,
    required this.coordinates,
    required this.address, // Address in the constructor
    this.battery,
    this.batteryVoltage,
    this.gwid,
    this.humidity0,
    this.humidity4,
    this.humidity,
    this.light0,
    this.rssirf,
    this.rain0,
    this.temperature0,
    this.temperature4,
    this.temperature,
    required this.timestamp,
    this.uv0,
    this.winddirection0,
    this.winddirection0Offset,
    this.windspeedAvg0,
    this.windspeedMax0,
    this.bootCount,
  });

  // Factory for creating WeatherStation objects from JSON
  factory WeatherStation.fromJson(String location, Map<String, dynamic> json) {
    final coordinates = LatLng(json['y'] ?? 0.0, json['x'] ?? 0.0);
    return WeatherStation(
      location: location,
      coordinates: coordinates,
      address: json['Adresse']?.toString() ?? "Unknown Address", // Simulated Address
      battery: json['Battery']?.toDouble(),
      batteryVoltage: json['BatteryVoltage']?.toDouble(),
      gwid: json['GWID'],
      humidity0: json['Humidity0']?.toDouble(),
      humidity4: json['Humidity4']?.toDouble(),
      humidity: json['humidity']?.toDouble(),
      light0: json['Light0']?.toDouble(),
      rssirf: json['RSSIRF']?.toDouble(),
      rain0: json['Rain0']?.toDouble(),
      temperature0: json['Temperature0']?.toDouble(),
      temperature4: json['Temperature4']?.toDouble(),
      temperature: json['temperature']?.toDouble(),
      timestamp: json['Time'] ?? 'N/A',
      uv0: json['UV0']?.toDouble(),
      winddirection0: json['Winddirection0']?.toDouble(),
      winddirection0Offset: json['Winddirection0Offset']?.toDouble(),
      windspeedAvg0: json['WindspeedAvg0']?.toDouble(),
      windspeedMax0: json['WindspeedMax0']?.toDouble(),
      bootCount: json['BootCount']?.toInt(),
    );
  }

  String getTemperature() {
    return temperature != null
        ? '${temperature}°C'
        : temperature0 != null
            ? '${temperature0}°C'
            : temperature4 != null
                ? '${temperature4}°C'
                : 'N/A';
  }

  String getHumidity() {
    return humidity != null
        ? '${humidity}%'
        : humidity0 != null
            ? '${humidity0}%'
            : humidity4 != null
                ? '${humidity4}%'
                : 'N/A';
  }

  String getRain() {
    return rain0 != null ? '${rain0} mm' : 'N/A';
  }

  String getLight() {
    return light0 != null ? '${light0} lux' : 'N/A';
  }

  String getRSSI() {
    return rssirf != null ? '${rssirf} dBm' : 'N/A';
  }

  String getWindSpeed() {
    return windspeedAvg0 != null
        ? '${windspeedAvg0} m/s'
        : windspeedMax0 != null
            ? '${windspeedMax0} m/s'
            : 'N/A';
  }

  String getWindDirection() {
    return winddirection0 != null
        ? '${winddirection0}°'
        : winddirection0Offset != null
            ? '${winddirection0Offset}°'
            : 'N/A';
  }

  String getUVIndex() {
    return uv0 != null ? '$uv0' : 'N/A';
  }

  String getBatteryStatus() {
    return battery != null
        ? '$battery%'
        : batteryVoltage != null
            ? '${batteryVoltage}V'
            : 'N/A';
  }
}

class MyMapWidget extends StatefulWidget {
  const MyMapWidget({super.key});

  @override
  _MyMapWidgetState createState() => _MyMapWidgetState();
}

class _MyMapWidgetState extends State<MyMapWidget> {
  LatLng? _currentPosition;
  late MapController _mapController;
  List<WeatherStation> _weatherStations = [];
  List<WeatherStation> _filteredWeatherStations = [];
  Timer? _timer;
  TextEditingController _searchController = TextEditingController();
  bool _isLoading = true;

  Map<String, bool> _filterOptions = {
    'Temperature': true,
    'Humidity': true,
    'Rain': true,
    'Wind': true,
    'Light': true,
    'UV': true,
    'Battery': true,
    'RSSI': true,
  };

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    loadWeatherDataFromAPI();

    _timer = Timer.periodic(const Duration(seconds: 30), (Timer t) {
      loadWeatherDataFromAPI();
    });

    _searchController.addListener(_filterWeatherStations);
  }

  Future<void> loadWeatherDataFromAPI() async {
    final apiUrl = 'http://localhost:8000/api/data';

    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final stations = data.entries.map((entry) {
          return WeatherStation.fromJson(entry.key, entry.value);
        }).toList();

        if (mounted) {
          setState(() {
            _weatherStations = stations;
            _filteredWeatherStations = stations;
            _isLoading = false;
          });
        }
      } else {
        print('Error loading data: ${response.statusCode}');
      }
    } catch (e) {
      print('Error loading data: $e');
    }
  }

  void _filterWeatherStations() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      _filteredWeatherStations = query.isEmpty
          ? _weatherStations
          : _weatherStations
              .where((station) =>
                  station.location.toLowerCase().contains(query) ||
                  station.address.toLowerCase().contains(query))
              .toList();
    });
  }

  void _openFilterPanel() {
    showModalBottomSheet(
        context: context,
        builder: (BuildContext context) {
          return StatefulBuilder(
              builder: (BuildContext context, StateSetter setModalState) {
            return SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const ListTile(title: Text('Filter Optionen')),
                  _buildFilterCheckbox('Temperature', setModalState),
                  _buildFilterCheckbox('Humidity', setModalState),
                  _buildFilterCheckbox('Rain', setModalState),
                  _buildFilterCheckbox('Wind', setModalState),
                  _buildFilterCheckbox('Light', setModalState),
                  _buildFilterCheckbox('UV', setModalState),
                  _buildFilterCheckbox('Battery', setModalState),
                  _buildFilterCheckbox('RSSI', setModalState),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      setState(() {});
                    },
                    child: const Text('Filter anwenden'),
                  ),
                ],
              ),
            );
          });
        });
  }

  CheckboxListTile _buildFilterCheckbox(
      String label, StateSetter setModalState) {
    return CheckboxListTile(
      title: Text('$label anzeigen'),
      value: _filterOptions[label],
      onChanged: (bool? value) {
        setModalState(() {
          _filterOptions[label] = value!;
        });
      },
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        scrolledUnderElevation: 0,
        elevation: 1,
        title: const Text('HS-Mannheim Wetterstationen Overview'),
      ),
      body: Row(
        children: [
          // Map Section
          Expanded(
            flex: 2,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.brown[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: const LatLng(49.4882, 8.467),
                    initialZoom: 12.0,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                      userAgentPackageName: 'com.example.app',
                    ),
                    MarkerLayer(
                      markers: _filteredWeatherStations.map((station) {
                        return Marker(
                          point: station.coordinates,
                          width: 80,
                          height: 80,
                          child: GestureDetector(
                            onTap: () {
                              _showStationPopup(context, station);
                            },
                            child: const Icon(
                              Icons.location_on,
                              color: Colors.blue,
                              size: 40,
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // List Section
          Expanded(
            flex: 1,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          decoration: const InputDecoration(
                            labelText: 'Suche nach Wetterstationen',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.filter_list),
                        onPressed: _openFilterPanel,
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Expanded(
                    child: _isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : _filteredWeatherStations.isEmpty
                            ? const Center(child: Text('Keine Wetterstationen gefunden'))
                            : ListView.builder(
                                itemCount: _filteredWeatherStations.length,
                                itemBuilder: (context, index) {
                                  final station = _filteredWeatherStations[index];
                                  return ListTile(
                                    leading: const Icon(Icons.thermostat, color: Colors.blue),
                                    title: Text(station.address), // Show the address as the main title
                                    subtitle: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Location: ${station.location}'), // Location as a subtitle
                                        Text('Koordinaten: (${station.coordinates.latitude}, ${station.coordinates.longitude})'),
                                        Text('Zeitstempel: ${station.timestamp}'),
                                        if (_filterOptions['Temperature']!) Text('Temperatur: ${station.getTemperature()}'),
                                        if (_filterOptions['Humidity']!) Text('Luftfeuchtigkeit: ${station.getHumidity()}'),
                                        if (_filterOptions['Rain']!) Text('Regen: ${station.getRain()}'),
                                        if (_filterOptions['Light']!) Text('Licht: ${station.getLight()}'),
                                        if (_filterOptions['Wind']!) Text('Windrichtung: ${station.getWindDirection()} | Windgeschwindigkeit: ${station.getWindSpeed()}'),
                                        if (_filterOptions['UV']!) Text('UV-Index: ${station.getUVIndex()}'),
                                        if (_filterOptions['Battery']!) Text('Batterie: ${station.getBatteryStatus()}'),
                                        if (_filterOptions['RSSI']!) Text('RSSI: ${station.getRSSI()}'),
                                      ],
                                    ),
                                    isThreeLine: true,
                                  );
                                },
                              ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showStationPopup(BuildContext context, WeatherStation station) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(station.location),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Adresse: ${station.address}'),
            Text('Koordinaten: (${station.coordinates.latitude}, ${station.coordinates.longitude})'),
            Text('Zeitstempel: ${station.timestamp}'),
            if (_filterOptions['Temperature']!) Text('Temperatur: ${station.getTemperature()}'),
            if (_filterOptions['Humidity']!) Text('Luftfeuchtigkeit: ${station.getHumidity()}'),
            if (_filterOptions['Rain']!) Text('Regen: ${station.getRain()}'),
            if (_filterOptions['Light']!) Text('Licht: ${station.getLight()}'),
            if (_filterOptions['Wind']!) Text('Windrichtung: ${station.getWindDirection()} | Windgeschwindigkeit: ${station.getWindSpeed()}'),
            if (_filterOptions['UV']!) Text('UV-Index: ${station.getUVIndex()}'),
            if (_filterOptions['Battery']!) Text('Batterie: ${station.getBatteryStatus()}'),
            if (_filterOptions['RSSI']!) Text('RSSI: ${station.getRSSI()}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Schließen'),
          ),
        ],
      ),
    );
  }
}

void main() {
  runApp(const MaterialApp(
    home: MyMapWidget(),
  ));
}

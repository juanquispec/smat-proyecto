import 'package:flutter/material.dart';
import 'models/estacion.dart';
import 'services/api_service.dart';
import 'screens/crear_estacion.dart';

void main() {
  runApp(const SMATApp());
}

class SMATApp extends StatelessWidget {
  const SMATApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SMAT Mobile',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  final ApiService apiService = ApiService();

  @override
  void initState() {
    super.initState();
    futureEstaciones = apiService.fetchEstaciones();
  }

  void _refrescarLista() {
    setState(() {
      futureEstaciones = apiService.fetchEstaciones();
    });
  }

  // --- DIÁLOGO PARA EDITAR (Lab 6.2) ---
  void _mostrarDialogoEditar(Estacion est) {
    final nombreCtrl = TextEditingController(text: est.nombre);
    final ubicacionCtrl = TextEditingController(text: est.ubicacion);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Editar Estación'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nombreCtrl, decoration: const InputDecoration(labelText: 'Nombre')),
              TextField(controller: ubicacionCtrl, decoration: const InputDecoration(labelText: 'Ubicación')),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context); // Cierra el cuadro
                bool exito = await apiService.editarEstacion(est.id, nombreCtrl.text, ubicacionCtrl.text);
                if (exito) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Estación editada'), backgroundColor: Colors.green));
                  _refrescarLista();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al editar'), backgroundColor: Colors.red));
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        );
      }
    );
  }

  // --- DIÁLOGO PARA ELIMINAR (Lab 6.2) ---
  void _confirmarEliminar(int id) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Eliminar estación?'),
        content: const Text('Esta acción borrará la estación permanentemente.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              Navigator.pop(context); // Cierra el cuadro
              bool exito = await apiService.eliminarEstacion(id);
              if (exito) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Estación eliminada'), backgroundColor: Colors.orange));
                _refrescarLista();
              }
            },
            child: const Text('Eliminar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  // --- RETO: DETERMINAR COLOR DEL ÍCONO ---
  Color _obtenerColorRiesgo(String nivel) {
    if (nivel == "PELIGRO") return Colors.red;
    if (nivel == "ALERTA") return Colors.orange;
    if (nivel == "NORMAL") return Colors.green;
    return Colors.grey; // Gris si no tiene lecturas
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        backgroundColor: Colors.blueAccent,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refrescarLista)
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          // Lab 7.1: Indicador visual de progreso
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } 
          // Lab 7.1: Manejo de errores de red (UX)
          else if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.wifi_off, size: 60, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text('Error: ${snapshot.error}', textAlign: TextAlign.center),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: _refrescarLista, child: const Text('Reintentar'))
                ],
              )
            );
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No hay estaciones registradas.'));
          } else {
            return ListView.builder(
              itemCount: snapshot.data!.length,
              itemBuilder: (context, index) {
                final est = snapshot.data![index];
                
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  child: ListTile(
                    // RETO: Evaluamos el riesgo de cada estación para pintar el ícono
                    leading: FutureBuilder<String>(
                      future: apiService.obtenerNivelRiesgo(est.id),
                      builder: (context, riesgoSnapshot) {
                        Color iconColor = Colors.grey;
                        if (riesgoSnapshot.hasData) {
                          iconColor = _obtenerColorRiesgo(riesgoSnapshot.data!);
                        }
                        return Icon(Icons.satellite_alt, color: iconColor, size: 30);
                      }
                    ),
                    title: Text(est.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('ID: ${est.id} | Ubicación: ${est.ubicacion}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.edit, color: Colors.blue),
                          onPressed: () => _mostrarDialogoEditar(est),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete, color: Colors.red),
                          onPressed: () => _confirmarEliminar(est.id),
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final resultado = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const CrearEstacionScreen()),
          );
          if (resultado == true) _refrescarLista();
        },
        tooltip: 'Agregar Estación',
        child: const Icon(Icons.add),
      ),
    );
  }
}
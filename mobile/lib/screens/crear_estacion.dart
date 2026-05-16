import 'package:flutter/material.dart';
// Ajusta esta ruta si guardaste api_service en la carpeta services
import '../services/api_service.dart'; 

class CrearEstacionScreen extends StatefulWidget {
  const CrearEstacionScreen({super.key});

  @override
  State<CrearEstacionScreen> createState() => _CrearEstacionScreenState();
}

class _CrearEstacionScreenState extends State<CrearEstacionScreen> {
  // Controladores para leer lo que el usuario escribe
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _nombreController = TextEditingController();
  final TextEditingController _ubicacionController = TextEditingController();
  
  bool _isLoading = false;

  void _guardarEstacion() async {
    setState(() => _isLoading = true);

    int id = int.tryParse(_idController.text) ?? 0;
    String nombre = _nombreController.text;
    String ubicacion = _ubicacionController.text;

    // Llamamos al servicio que acabamos de actualizar
    bool exito = await ApiService().crearEstacion(id, nombre, ubicacion);

    setState(() => _isLoading = false);

    if (exito) {
      // Si se guardó bien, mostramos un mensaje y regresamos a la pantalla anterior
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Estación creada con éxito'), backgroundColor: Colors.green),
        );
        Navigator.pop(context, true); // Regresa "true" para avisar que hubo un cambio
      }
    } else {
      // Si hubo error (ej. el ID ya existe)
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error al crear la estación. Verifica el ID.'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nueva Estación'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _idController,
              decoration: const InputDecoration(labelText: 'ID de Estación (Número)'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _nombreController,
              decoration: const InputDecoration(labelText: 'Nombre de Estación'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _ubicacionController,
              decoration: const InputDecoration(labelText: 'Ubicación'),
            ),
            const SizedBox(height: 30),
            _isLoading 
              ? const CircularProgressIndicator()
              : ElevatedButton(
                  onPressed: _guardarEstacion,
                  style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
                  child: const Text('Guardar Estación', style: TextStyle(fontSize: 18)),
                )
          ],
        ),
      ),
    );
  }
}
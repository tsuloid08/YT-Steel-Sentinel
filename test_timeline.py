# Script de prueba para verificar las mejoras de timeline
import logging

# Configurar logging para pruebas
logging.basicConfig(level=logging.DEBUG)

def test_format_time():
    """Prueba la función format_time con diferentes valores"""
    
    def format_time(seconds):
        if seconds is None or seconds < 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    # Casos de prueba
    test_cases = [
        (0, "00:00"),
        (30, "00:30"),
        (60, "01:00"),
        (90, "01:30"),
        (218, "03:38"),
        (3661, "61:01"),
        (-1, "00:00"),
        (None, "00:00"),
        (0.5, "00:00"),
        (59.9, "00:59")
    ]
    
    print("Probando función format_time:")
    for input_val, expected in test_cases:
        result = format_time(input_val)
        status = "✓" if result == expected else "✗"
        print(f"{status} format_time({input_val}) = {result} (esperado: {expected})")

if __name__ == "__main__":
    test_format_time()
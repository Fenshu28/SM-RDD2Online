#!/usr/bin/env python3
"""
RDR2 Session Manager - Build Script
Compila el proyecto a un ejecutable portable con PyInstaller
"""

import os
import sys
import subprocess
import hashlib
import shutil
from pathlib import Path
import argparse

# Configuración del build
BUILD_CONFIG = {
    "app_name": "RDR2_Session_Manager",
    "source_file": "rdr2_session_manager.py",
    "icon_file": "icon.ico",  # Opcional
    "version": "1.0.0"
}

def print_banner():
    """Muestra el banner del script"""
    print("🎮 RDR2 Session Manager - Build Script")
    print("=" * 50)
    print(f"📦 Building: {BUILD_CONFIG['app_name']}")
    print(f"📂 Source: {BUILD_CONFIG['source_file']}")
    print(f"🔢 Version: {BUILD_CONFIG['version']}")
    print("=" * 50)

def check_requirements():
    """Verifica que estén los archivos necesarios"""
    errors = []
    
    # Verificar archivo fuente
    if not Path(BUILD_CONFIG['source_file']).exists():
        errors.append(f"❌ No se encontró: {BUILD_CONFIG['source_file']}")
    
    # Verificar PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("❌ PyInstaller no está instalado. Ejecuta: pip install pyinstaller")
    
    if errors:
        print("\n".join(errors))
        return False
    
    print("✅ Todos los requisitos están cumplidos")
    return True

def calculate_md5(file_path):
    """Calcula el hash MD5 de un archivo"""
    print(f"🔐 Calculando MD5 para: {file_path.name}")
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def clean_build_dirs():
    """Limpia directorios de builds anteriores"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"🧹 Limpiando: {dir_name}")
            shutil.rmtree(dir_name)

def build_executable(clean=True, debug=False):
    """Compila el ejecutable con PyInstaller"""
    
    if clean:
        clean_build_dirs()
    
    print("🔨 Iniciando compilación...")
    
    # Comando base de PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                              # Un solo archivo
        "--noconsole",                           # Sin ventana de consola
        f"--name={BUILD_CONFIG['app_name']}",    # Nombre del ejecutable
        "--optimize=2",                          # Optimización máxima
        "--clean",                               # Limpiar cache
    ]
    
    # Agregar icono si existe
    if Path(BUILD_CONFIG['icon_file']).exists():
        cmd.append(f"--icon={BUILD_CONFIG['icon_file']}")
        print(f"🎨 Usando icono: {BUILD_CONFIG['icon_file']}")
    
    # Modo debug (mantiene consola)
    if debug:
        cmd.remove("--noconsole")
        cmd.append("--debug=all")
        print("🐛 Modo debug activado")
    
    # Archivo fuente
    cmd.append(BUILD_CONFIG['source_file'])
    
    try:
        print(f"📝 Comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print("📋 PyInstaller output:")
            print(result.stdout)
        
        print("✅ Compilación exitosa!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la compilación:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        return False

def create_checksums_and_info():
    """Crea archivos de verificación y información"""
    exe_path = Path(f"dist/{BUILD_CONFIG['app_name']}.exe")
    
    if not exe_path.exists():
        print(f"❌ No se encontró el ejecutable: {exe_path}")
        return None
    
    # Calcular MD5
    md5_hash = calculate_md5(exe_path)
    
    # Crear archivo MD5
    md5_file = exe_path.with_suffix('.exe.md5')
    with open(md5_file, 'w') as f:
        f.write(f"{md5_hash}  {BUILD_CONFIG['app_name']}.exe\n")
    
    # Calcular SHA256 también (más seguro)
    print(f"🔐 Calculando SHA256 para: {exe_path.name}")
    hash_sha256 = hashlib.sha256()
    with open(exe_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    sha256_hash = hash_sha256.hexdigest()
    
    # Crear archivo SHA256
    sha256_file = exe_path.with_suffix('.exe.sha256')
    with open(sha256_file, 'w') as f:
        f.write(f"{sha256_hash}  {BUILD_CONFIG['app_name']}.exe\n")
    
    # Información del archivo
    size_bytes = exe_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    
    # Crear archivo de información
    info_content = f"""# {BUILD_CONFIG['app_name']} - Build Info

## 📦 Archivo
- **Nombre:** {BUILD_CONFIG['app_name']}.exe
- **Tamaño:** {size_mb:.2f} MB ({size_bytes:,} bytes)
- **Versión:** {BUILD_CONFIG['version']}

## 🔐 Checksums
- **MD5:** {md5_hash}
- **SHA256:** {sha256_hash}

## ✅ Verificación
### Windows (CMD):
```cmd
certutil -hashfile {BUILD_CONFIG['app_name']}.exe MD5
certutil -hashfile {BUILD_CONFIG['app_name']}.exe SHA256
```

### PowerShell:
```powershell
Get-FileHash -Algorithm MD5 {BUILD_CONFIG['app_name']}.exe
Get-FileHash -Algorithm SHA256 {BUILD_CONFIG['app_name']}.exe
```

### Linux/Mac:
```bash
md5sum {BUILD_CONFIG['app_name']}.exe
sha256sum {BUILD_CONFIG['app_name']}.exe
```
"""
    
    info_file = Path("dist/BUILD_INFO.md")
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    return {
        'exe_path': exe_path,
        'size_mb': size_mb,
        'md5': md5_hash,
        'sha256': sha256_hash,
        'files': [exe_path, md5_file, sha256_file, info_file]
    }

def print_summary(build_info):
    """Muestra resumen del build"""
    if not build_info:
        return
    
    print("\n🎉 ¡Build completado exitosamente!")
    print("=" * 50)
    print(f"📦 Ejecutable: {build_info['exe_path']}")
    print(f"📏 Tamaño: {build_info['size_mb']:.2f} MB")
    print(f"🔐 MD5: {build_info['md5']}")
    print(f"🔐 SHA256: {build_info['sha256'][:16]}...")
    print("\n📄 Archivos generados:")
    for file_path in build_info['files']:
        print(f"   • {file_path}")
    
    print("\n🚀 Para crear release en GitHub:")
    print("1. git add .")
    print("2. git commit -m 'Release v1.0.0'")
    print("3. git tag v1.0.0")
    print("4. git push origin main")
    print("5. git push origin v1.0.0")

def main():
    parser = argparse.ArgumentParser(description="Build RDR2 Session Manager")
    parser.add_argument("--no-clean", action="store_true", 
                       help="No limpiar directorios de build")
    parser.add_argument("--debug", action="store_true", 
                       help="Build en modo debug (con consola)")
    parser.add_argument("--check-only", action="store_true", 
                       help="Solo verificar requisitos")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)
    
    if args.check_only:
        print("✅ Verificación completada. Todo está listo para el build.")
        return
    
    # Compilar
    if not build_executable(clean=not args.no_clean, debug=args.debug):
        sys.exit(1)
    
    # Crear archivos de verificación
    build_info = create_checksums_and_info()
    
    # Mostrar resumen
    print_summary(build_info)

if __name__ == "__main__":
    main()
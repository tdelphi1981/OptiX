#!/usr/bin/env python3
"""
OptiX Documentation Build Script

This script automates the documentation building process for the OptiX framework.
It handles dependency installation, builds multiple formats, and provides
helpful feedback during the process.

Usage:
    python build_docs.py [--format html|pdf|all] [--serve] [--clean] [--check]
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a styled header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

def run_command(command, description, check=True):
    """Run a shell command with pretty output."""
    print(f"{Colors.OKCYAN}🔄 {description}...{Colors.ENDC}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        
        if result.returncode == 0:
            print_success(f"{description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print_error(f"{description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
                
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with exit code {e.returncode}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False
    except Exception as e:
        print_error(f"{description} failed: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("Checking Dependencies")
    
    dependencies = [
        ("python", "Python interpreter"),
        ("pip", "Python package installer"),
        ("make", "Build automation tool")
    ]
    
    all_good = True
    
    for cmd, description in dependencies:
        if run_command(f"which {cmd}", f"Checking {description}", check=False):
            pass
        else:
            all_good = False
            print_error(f"{description} not found")
    
    # Check Python version
    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        version = result.stdout.strip()
        print_info(f"Found {version}")
        
        # Extract version number
        version_parts = version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        if major < 3 or (major == 3 and minor < 12):
            print_warning(f"Python 3.12+ recommended, found {version}")
        else:
            print_success(f"Python version compatible")
    
    return all_good

def install_dependencies():
    """Install documentation dependencies."""
    print_header("Installing Dependencies")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    return run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    )

def clean_build():
    """Clean the build directory."""
    print_header("Cleaning Build Directory")
    
    return run_command(
        "make clean",
        "Removing previous build files"
    )

def build_html():
    """Build HTML documentation."""
    print_header("Building HTML Documentation")
    
    start_time = time.time()
    success = run_command(
        "make html",
        "Building HTML documentation"
    )
    build_time = time.time() - start_time
    
    if success:
        print_success(f"HTML documentation built in {build_time:.2f} seconds")
        html_path = Path("build/html/index.html").absolute()
        print_info(f"Open file://{html_path} in your browser")
    
    return success

def build_pdf():
    """Build PDF documentation."""
    print_header("Building PDF Documentation")
    
    # Check LaTeX installation
    latex_available = run_command(
        "which pdflatex",
        "Checking LaTeX installation",
        check=False
    )
    
    if not latex_available:
        print_warning("LaTeX not found. PDF generation requires a LaTeX distribution.")
        print_info("Install LaTeX: https://www.latex-project.org/get/")
        return False
    
    start_time = time.time()
    success = run_command(
        "make latexpdf",
        "Building PDF documentation"
    )
    build_time = time.time() - start_time
    
    if success:
        print_success(f"PDF documentation built in {build_time:.2f} seconds")
        pdf_path = Path("build/latex/OptiX.pdf").absolute()
        if pdf_path.exists():
            print_info(f"PDF saved to: {pdf_path}")
        else:
            print_warning("PDF file not found in expected location")
    
    return success

def serve_documentation():
    """Serve documentation locally."""
    print_header("Serving Documentation")
    
    html_dir = Path("build/html")
    if not html_dir.exists():
        print_error("HTML documentation not found. Build it first with --format html")
        return False
    
    print_info("Starting local server on http://localhost:8080")
    print_info("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            "python", "-m", "http.server", "8080"
        ], cwd=html_dir, check=True)
    except KeyboardInterrupt:
        print_success("Server stopped")
        return True
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return False

def check_documentation():
    """Check documentation for issues."""
    print_header("Checking Documentation Quality")
    
    checks = [
        ("make linkcheck", "Checking external links"),
        ("make coverage", "Checking documentation coverage"),
    ]
    
    all_passed = True
    
    for command, description in checks:
        if not run_command(command, description, check=False):
            all_passed = False
    
    if all_passed:
        print_success("All documentation checks passed")
    else:
        print_warning("Some documentation checks failed")
    
    return all_passed

def generate_api_docs():
    """Generate API documentation from source code."""
    print_header("Generating API Documentation")
    
    # Check if source directory exists
    src_dir = Path("../src")
    if not src_dir.exists():
        print_error("Source directory not found. Run from docs/ directory.")
        return False
    
    return run_command(
        "make apidoc",
        "Generating API documentation from source code"
    )

def show_statistics():
    """Show documentation statistics."""
    print_header("Documentation Statistics")
    
    run_command("make stats", "Calculating documentation statistics", check=False)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Build OptiX documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_docs.py                    # Build HTML documentation
  python build_docs.py --format all       # Build HTML and PDF
  python build_docs.py --serve           # Build HTML and serve locally
  python build_docs.py --clean --format pdf  # Clean and build PDF
  python build_docs.py --check           # Check documentation quality
        """
    )
    
    parser.add_argument(
        '--format',
        choices=['html', 'pdf', 'all'],
        default='html',
        help='Documentation format to build (default: html)'
    )
    
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Serve documentation locally after building HTML'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build directory before building'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check documentation for issues'
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install required dependencies'
    )
    
    parser.add_argument(
        '--apidoc',
        action='store_true',
        help='Generate API documentation from source code'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show documentation statistics'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("   ___       _   _ __  __")
    print("  / _ \\ _ __| |_(_)  \\/  |")
    print(" | | | | '_ \\ __| | |\\/| |")
    print(" | |_| | |_) | |_| | |  | |")
    print("  \\___/| .__/ \\__|_|_|  |_|")
    print("       |_|")
    print()
    print("Mathematical Optimization Framework")
    print("Documentation Build System")
    print(f"{Colors.ENDC}")
    
    # Change to docs directory if not already there
    if not Path("source").exists():
        docs_dir = Path(__file__).parent
        os.chdir(docs_dir)
        print_info(f"Changed to directory: {docs_dir}")
    
    # Check dependencies
    if not check_dependencies():
        print_error("Dependency check failed")
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print_error("Failed to install dependencies")
            sys.exit(1)
    
    # Clean if requested
    if args.clean:
        if not clean_build():
            print_error("Failed to clean build directory")
            sys.exit(1)
    
    # Generate API docs if requested
    if args.apidoc:
        if not generate_api_docs():
            print_error("Failed to generate API documentation")
            sys.exit(1)
    
    # Show statistics if requested
    if args.stats:
        show_statistics()
        return
    
    # Check documentation if requested
    if args.check:
        if not check_documentation():
            sys.exit(1)
        return
    
    # Build documentation
    success = True
    
    if args.format in ['html', 'all']:
        if not build_html():
            success = False
    
    if args.format in ['pdf', 'all']:
        if not build_pdf():
            success = False
    
    if not success:
        print_error("Documentation build failed")
        sys.exit(1)
    
    # Serve if requested
    if args.serve and args.format in ['html', 'all']:
        serve_documentation()
    
    print_header("Build Complete")
    print_success("OptiX documentation build completed successfully!")
    
    if args.format in ['html', 'all']:
        html_path = Path("build/html/index.html").absolute()
        print_info(f"HTML: file://{html_path}")
    
    if args.format in ['pdf', 'all']:
        pdf_path = Path("build/latex/OptiX.pdf").absolute()
        if pdf_path.exists():
            print_info(f"PDF: {pdf_path}")

if __name__ == "__main__":
    main()
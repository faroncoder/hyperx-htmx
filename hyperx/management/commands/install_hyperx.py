
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
..opt.hyperx.core_install_hyperx import *



class Command(BaseCommand):
    help = 'Automatically install HyperX configuration into Django settings.py'

    def add_arguments(self, parser):
        parser.add_argument(
            '--settings-file',
            type=str,
            help='Path to the settings.py file to modify (default: auto-detect)',
        )
        parser.add_argument(
            '--no-backup',
            action='store_true',
            help='Skip creating a backup of the original settings file',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force installation even if HyperX is already configured',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually modifying files',
        )
        parser.add_argument(
            '--no-cleanup',
            action='store_true',
            help='Skip removing management command files after installation',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 HyperX Installation Management Command')
        )
        self.stdout.write('=' * 50)

        # Determine settings file path
        settings_path = self._get_settings_path(options['settings_file'])
        if not settings_path:
            raise CommandError(
                "Could not find settings.py file. Please specify with --settings-file"
            )

        self.stdout.write(f"📁 Settings file: {settings_path}")

        # Dry run mode
        if options['dry_run']:
            self._perform_dry_run(settings_path)
            return

        # Create installer
        installer = HyperXInstaller(settings_path)
        
        # Check if already installed (unless forced)
        if not options['force'] and self._is_already_installed(settings_path):
            self.stdout.write(
                self.style.WARNING("⚠️ HyperX appears to already be installed")
            )
            self.stdout.write("Use --force to reinstall")
            return

        # Perform installation
        try:
            success = installer.install(create_backup=not options['no_backup'])
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS("🎉 HyperX installation completed successfully!")
                )
                self._show_next_steps()
                
                # Clean up management commands unless --no-cleanup is specified
                if not options['no_cleanup']:
                    self._cleanup_management_commands()
            else:
                raise CommandError("Installation failed")
                
        except Exception as e:
            raise CommandError(f"Installation error: {str(e)}")

    def _get_settings_path(self, settings_file):
        """Determine the path to the settings file."""
        if settings_file:
            path = Path(settings_file)
            if not path.exists():
                self.stdout.write(
                    self.style.ERROR(f"❌ Settings file not found: {settings_file}")
                )
                return None
            return str(path)

        # Try to auto-detect from Django settings
        try:
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
            if settings_module:
                # Convert module path to file path
                module_parts = settings_module.split('.')
                settings_file = '/'.join(module_parts) + '.py'
                
                # Look in current directory and common locations
                possible_paths = [
                    settings_file,
                    f"./{settings_file}",
                    f"../{settings_file}",
                ]
                
                for path in possible_paths:
                    if Path(path).exists():
                        return str(Path(path).resolve())
        except:
            pass

        # Fallback to generic search
        return find_django_settings()

    def _is_already_installed(self, settings_path):
        """Check if HyperX is already configured in settings."""
        try:
            content = Path(settings_path).read_text()
            return ('hyperx' in content.lower() and 
                   'HYPERX_MIDDLEWARE' in content)
        except:
            return False

    def _perform_dry_run(self, settings_path):
        """Show what would be changed without modifying files."""
        self.stdout.write(
            self.style.WARNING("🔍 DRY RUN MODE - No files will be modified")
        )
        
        try:
            content = Path(settings_path).read_text()
            
            # Check what would be added
            changes = []
            
            if '"django_htmx"' not in content:
                changes.append("➕ Add 'django_htmx' to INSTALLED_APPS")
            if '"hyperx"' not in content:
                changes.append("➕ Add 'hyperx' to INSTALLED_APPS")
                
            if 'HtmxMiddleware' not in content:
                changes.append("➕ Add HtmxMiddleware to MIDDLEWARE")
            if 'HyperXMiddleware' not in content:
                changes.append("➕ Add HyperXMiddleware to MIDDLEWARE")
            if 'HyperXSecurityMiddleware' not in content:
                changes.append("➕ Add HyperXSecurityMiddleware to MIDDLEWARE")
                
            if 'HYPERX_MIDDLEWARE' not in content:
                changes.append("➕ Add HYPERX_MIDDLEWARE configuration")
            if 'HYPERX_SECURITY' not in content:
                changes.append("➕ Add HYPERX_SECURITY configuration")
            
            if changes:
                self.stdout.write("\n📋 Planned changes:")
                for change in changes:
                    self.stdout.write(f"   {change}")
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ No changes needed - HyperX already configured")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error reading settings file: {e}")
            )

    def _show_next_steps(self):
        """Display next steps after successful installation."""
        self.stdout.write("\n📋 Next Steps:")
        self.stdout.write("1. Run migrations if needed:")
        self.stdout.write("   python manage.py migrate")
        self.stdout.write("\n2. In your templates, load HyperX tags:")
        self.stdout.write("   {% load hyperx %}")
        self.stdout.write("\n3. Use HyperX in your templates:")
        self.stdout.write("   {% hx %}")
        self.stdout.write("     <hx:button get='your_view' target='#content' />")
        self.stdout.write("   {% endhx %}")
        self.stdout.write("\n4. Check the documentation for more examples!")
        self.stdout.write(
            self.style.HTTP_INFO("\n📚 Documentation: https://github.com/faroncoder/hyperx-htmx")
        )
        self.stdout.write("\n💡 Note: A detailed disclosure of all changes made")
        self.stdout.write("   has been added to the end of your settings.py file.")

    def _cleanup_management_commands(self):
        """Remove HyperX management command files to avoid cluttering user's project."""
        import shutil
        from pathlib import Path
        
        self.stdout.write("\n🧹 Cleaning up installation files...")
        
        try:
            # Find the hyperx package management commands directory
            import hyperx
            hyperx_path = Path(hyperx.__file__).parent
            management_dir = hyperx_path / 'management'
            
            if management_dir.exists():
                # List what will be removed
                commands_dir = management_dir / 'commands'
                removed_files = []
                
                if commands_dir.exists():
                    for cmd_file in commands_dir.glob('*.py'):
                        if cmd_file.name != '__init__.py':
                            removed_files.append(cmd_file.name)
                
                # Remove the entire management directory
                shutil.rmtree(management_dir)
                
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Removed HyperX installation files:")
                )
                for file_name in removed_files:
                    self.stdout.write(f"      • {file_name}")
                self.stdout.write("   • management/ directory")
                self.stdout.write("\n   💡 This keeps your Django project clean and professional")
            else:
                self.stdout.write("   ℹ️ Installation files already cleaned up")
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"   ⚠️ Could not remove installation files: {e}")
            )
            self.stdout.write("   💡 You can manually delete hyperx/management/ directory")
            self.stdout.write("   (This doesn't affect HyperX functionality)")
            
        self.stdout.write(f"\n🎯 {self.style.SUCCESS('HyperX is now ready to use in your Django project!')}")
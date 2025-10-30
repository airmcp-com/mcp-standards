#!/usr/bin/env python3
"""V2 System Deployment Script

One-click deployment and setup script for V2 pattern extraction system.
This script handles all necessary setup steps for Claude Code integration.
"""

import sys
import asyncio
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_standards.utils.v2_status import check_v2_status, V2StatusChecker
from src.mcp_standards.migration.v1_to_v2_migration import migrate_v1_to_v2


class V2Deployer:
    """Automated V2 system deployment"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.deployment_steps = []

    def log(self, message: str, level: str = "info"):
        """Log deployment messages"""
        if not self.verbose:
            return

        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "step": "🔧"
        }

        emoji = emoji_map.get(level, "📋")
        print(f"{emoji} {message}")

    async def deploy(self,
                    migrate_v1: bool = True,
                    start_agentdb: bool = True,
                    verify_installation: bool = True) -> bool:
        """
        Deploy V2 system with all necessary components

        Args:
            migrate_v1: Whether to migrate existing V1 patterns
            start_agentdb: Whether to start AgentDB HTTP server
            verify_installation: Whether to run verification tests

        Returns:
            True if deployment successful
        """
        self.log("🚀 Starting V2 Pattern Extraction System Deployment")
        self.log("=" * 60)

        try:
            # Step 1: Check prerequisites
            self.log("Checking prerequisites...", "step")
            if not await self._check_prerequisites():
                return False

            # Step 2: Start AgentDB server if needed
            if start_agentdb:
                self.log("Starting AgentDB HTTP server...", "step")
                if not await self._start_agentdb_server():
                    self.log("AgentDB server start failed - continuing with manual setup", "warning")

            # Step 3: Install dependencies
            self.log("Installing Python dependencies...", "step")
            if not self._install_dependencies():
                return False

            # Step 4: Initialize V2 system
            self.log("Initializing V2 system...", "step")
            if not await self._initialize_v2_system():
                return False

            # Step 5: Migrate V1 patterns if requested
            if migrate_v1:
                self.log("Migrating V1 patterns to V2...", "step")
                migration_success = await self._migrate_v1_patterns()
                if not migration_success:
                    self.log("V1 migration failed - continuing without migration", "warning")

            # Step 6: Verify deployment
            if verify_installation:
                self.log("Verifying V2 system deployment...", "step")
                if not await self._verify_deployment():
                    return False

            # Step 7: Generate deployment report
            await self._generate_deployment_report()

            self.log("V2 deployment completed successfully!", "success")
            self.log("🎉 V2 Pattern Extraction System is ready for Claude Code integration")

            return True

        except Exception as e:
            self.log(f"Deployment failed: {e}", "error")
            return False

    async def _check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        checks = [
            ("Python 3.8+", self._check_python_version),
            ("Node.js for AgentDB", self._check_nodejs),
            ("Project structure", self._check_project_structure),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if await check_func() if asyncio.iscoroutinefunction(check_func) else check_func():
                    self.log(f"{check_name}: ✅", "success")
                else:
                    self.log(f"{check_name}: ❌", "error")
                    all_passed = False
            except Exception as e:
                self.log(f"{check_name}: ❌ {e}", "error")
                all_passed = False

        return all_passed

    def _check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        return version.major >= 3 and version.minor >= 8

    def _check_nodejs(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(["node", "--version"],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_project_structure(self) -> bool:
        """Check required project files exist"""
        required_files = [
            "src/mcp_standards/hooks/capture_hook_v2.py",
            "src/mcp_standards/memory/v2/agentdb_adapter_new.py",
            "agentdb_http_server.cjs"
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                self.log(f"Missing required file: {file_path}", "error")
                return False

        return True

    async def _start_agentdb_server(self) -> bool:
        """Start AgentDB HTTP server"""
        try:
            # Check if already running
            checker = V2StatusChecker()
            if await checker.check_agentdb_connectivity():
                self.log("AgentDB server already running", "success")
                return True

            # Start the server
            self.log("Launching AgentDB HTTP server...")
            proc = subprocess.Popen(
                ["node", "agentdb_http_server.cjs"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            for i in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                if await checker.check_agentdb_connectivity():
                    self.log("AgentDB server started successfully", "success")
                    return True

            self.log("AgentDB server did not start within timeout", "warning")
            return False

        except Exception as e:
            self.log(f"Failed to start AgentDB server: {e}", "warning")
            return False

    def _install_dependencies(self) -> bool:
        """Install required Python dependencies"""
        dependencies = ["aiohttp"]

        try:
            for dep in dependencies:
                self.log(f"Installing {dep}...")
                result = subprocess.run(
                    ["uv", "add", dep],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    self.log(f"Failed to install {dep}: {result.stderr}", "error")
                    return False

            self.log("All dependencies installed successfully", "success")
            return True

        except subprocess.TimeoutExpired:
            self.log("Dependency installation timed out", "error")
            return False
        except Exception as e:
            self.log(f"Dependency installation failed: {e}", "error")
            return False

    async def _initialize_v2_system(self) -> bool:
        """Initialize V2 system components"""
        try:
            # Test V2 system initialization
            from src.mcp_standards.hooks.capture_hook_v2 import HookCaptureSystemV2

            test_system = HookCaptureSystemV2()

            # Quick initialization test
            if await test_system._initialize_v2_system():
                self.log("V2 system initialization successful", "success")
                await test_system.close()
                return True
            else:
                self.log("V2 system initialization failed", "error")
                await test_system.close()
                return False

        except Exception as e:
            self.log(f"V2 system initialization error: {e}", "error")
            return False

    async def _migrate_v1_patterns(self) -> bool:
        """Migrate existing V1 patterns to V2"""
        try:
            v1_db_path = Path.home() / ".mcp-standards" / "knowledge.db"

            if not v1_db_path.exists():
                self.log("No V1 database found - skipping migration", "info")
                return True

            self.log(f"Migrating patterns from {v1_db_path}...")

            stats = await migrate_v1_to_v2(
                v1_db_path=str(v1_db_path),
                dry_run=False,
                backup_enabled=True
            )

            if stats.success_rate > 80:
                self.log(f"Migration successful: {stats.migrated_patterns}/{stats.total_v1_patterns} patterns", "success")
                return True
            else:
                self.log(f"Migration partially failed: {stats.success_rate:.1f}% success rate", "warning")
                return False

        except Exception as e:
            self.log(f"Migration failed: {e}", "error")
            return False

    async def _verify_deployment(self) -> bool:
        """Verify deployment is working correctly"""
        try:
            self.log("Running deployment verification...")

            # Check overall system health
            health = await check_v2_status()

            if health.overall_status == "healthy":
                self.log("All V2 components are healthy", "success")
                return True
            else:
                self.log(f"V2 system status: {health.overall_status}", "warning")
                self.log("Some components may need attention:", "warning")
                for rec in health.recommendations:
                    self.log(f"  {rec}", "info")
                return False

        except Exception as e:
            self.log(f"Verification failed: {e}", "error")
            return False

    async def _generate_deployment_report(self):
        """Generate deployment report"""
        self.log("\n📊 Deployment Report", "info")
        self.log("=" * 30)

        try:
            health = await check_v2_status()
            checker = V2StatusChecker()

            # Component status
            components = [
                health.agentdb_status,
                health.sqlite_status,
                health.hook_status,
                health.memory_status
            ]

            for status in components:
                status_emoji = "✅" if status.status == "healthy" else "⚠️" if status.status == "degraded" else "❌"
                self.log(f"{status_emoji} {status.component}: {status.message}")

            # Next steps
            self.log("\n🎯 Next Steps:", "info")
            self.log("1. Configure Claude Code to use V2 hooks")
            self.log("2. Test pattern extraction with real tool executions")
            self.log("3. Monitor system performance and pattern quality")
            self.log("4. Run 'python src/mcp_standards/utils/v2_status.py' for health checks")

        except Exception as e:
            self.log(f"Report generation failed: {e}", "error")


async def deploy_v2_system(
    migrate_v1: bool = True,
    start_agentdb: bool = True,
    verify: bool = True,
    verbose: bool = True
) -> bool:
    """
    Deploy V2 system with specified options

    Args:
        migrate_v1: Migrate existing V1 patterns
        start_agentdb: Start AgentDB HTTP server
        verify: Run verification tests
        verbose: Verbose logging

    Returns:
        True if deployment successful
    """
    deployer = V2Deployer(verbose=verbose)
    return await deployer.deploy(
        migrate_v1=migrate_v1,
        start_agentdb=start_agentdb,
        verify_installation=verify
    )


def main():
    """Main deployment entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy V2 Pattern Extraction System")
    parser.add_argument("--no-migrate", action="store_true", help="Skip V1 pattern migration")
    parser.add_argument("--no-agentdb", action="store_true", help="Don't start AgentDB server")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification tests")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    async def run_deployment():
        success = await deploy_v2_system(
            migrate_v1=not args.no_migrate,
            start_agentdb=not args.no_agentdb,
            verify=not args.no_verify,
            verbose=not args.quiet
        )

        if success:
            print("\n🎉 V2 deployment completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ V2 deployment failed - check logs above")
            sys.exit(1)

    asyncio.run(run_deployment())


if __name__ == "__main__":
    main()
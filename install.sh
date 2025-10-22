#!/bin/bash
# N5 ATS Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/vrijenattawar/ZoATS/main/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

INSTALL_DIR="/home/workspace/ZoATS"
N5_CORE_DIR="/home/workspace/N5"
BACKUP_DIR="/home/workspace/.n5-ats-backups"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 N5 ATS Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check/Install N5 Core
log_info "Checking for N5 Core..."
if [ ! -d "$N5_CORE_DIR" ] || [ ! -f "$N5_CORE_DIR/scripts/session_state_manager.py" ]; then
    log_warning "N5 Core not found. Installing..."
    curl -fsSL https://raw.githubusercontent.com/vrijenattawar/n5-core/main/install.sh | bash
    log_success "N5 Core installed"
else
    log_success "N5 Core found"
fi

# Step 2: Backup existing installation
if [ -d "$INSTALL_DIR" ]; then
    log_warning "Existing N5 ATS installation found"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    mkdir -p "$BACKUP_DIR"
    BACKUP_PATH="$BACKUP_DIR/zoats-$TIMESTAMP"
    log_info "Creating backup: $BACKUP_PATH"
    cp -r "$INSTALL_DIR" "$BACKUP_PATH"
    log_success "Backup created"
fi

# Step 3: Install N5 ATS
log_info "Installing N5 ATS..."

if [ -d "$INSTALL_DIR/.git" ]; then
    log_info "Updating existing repository..."
    cd "$INSTALL_DIR"
    git fetch origin --quiet
    git reset --hard origin/main
else
    log_info "Cloning repository..."
    rm -rf "$INSTALL_DIR"
    git clone https://github.com/vrijenattawar/ZoATS.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

log_success "Repository installed"

# Step 4: Create directories
log_info "Creating runtime directories..."
mkdir -p "$INSTALL_DIR"/{jobs,inbox_drop,logs,data}
log_success "Directories created"

# Step 5: Set permissions
log_info "Setting permissions..."
chmod +x "$INSTALL_DIR"/scripts/*.py 2>/dev/null || true
chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true
log_success "Permissions set"

# Step 6: Configuration
if [ ! -f "$INSTALL_DIR/config/settings.json" ]; then
    if [ -f "$INSTALL_DIR/config/settings.example.json" ]; then
        log_info "Creating default configuration..."
        cp "$INSTALL_DIR/config/settings.example.json" "$INSTALL_DIR/config/settings.json"
        log_success "Configuration created"
    fi
fi

# Step 7: Verify installation
log_info "Verifying installation..."

CHECKS_PASSED=0
CHECKS_TOTAL=4

[ -d "$INSTALL_DIR/workers" ] && ((CHECKS_PASSED++))
[ -d "$INSTALL_DIR/pipeline" ] && ((CHECKS_PASSED++))
[ -f "$INSTALL_DIR/config/commands.jsonl" ] && ((CHECKS_PASSED++))
[ -d "$INSTALL_DIR/schemas" ] && ((CHECKS_PASSED++))

if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    log_success "Installation verified ($CHECKS_PASSED/$CHECKS_TOTAL checks passed)"
else
    log_error "Installation incomplete ($CHECKS_PASSED/$CHECKS_TOTAL checks passed)"
    exit 1
fi

# Step 8: Display info
CURRENT_COMMIT=$(git rev-parse --short HEAD)
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "N5 ATS Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Version:    $CURRENT_VERSION"
echo "  Commit:     $CURRENT_COMMIT"
echo "  Location:   $INSTALL_DIR"
echo ""
echo "Next Steps:"
echo "  1. Configure: $INSTALL_DIR/config/settings.json"
echo "  2. Review docs: $INSTALL_DIR/docs/"
echo "  3. Start processing candidates!"
echo ""
log_success "Ready to hire!"

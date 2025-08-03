#!/bin/bash
set -e

# Detect version from latest git tag
VERSION=$(git tag --sort=-creatordate | head -n1 2>/dev/null || echo "v0.0.0")
GIT_DESCRIBE=$(git describe --tags --always 2>/dev/null || echo "$VERSION")

# If HEAD is not at the tag, append short hash
if [[ "$GIT_DESCRIBE" != "$VERSION" ]]; then
    SHORT_HASH=$(git rev-parse --short HEAD)
    VERSION="${VERSION}-${SHORT_HASH}"
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    VERSION="${VERSION}-dirty"
fi

echo "Detected version: $VERSION"

# Inject version into app/version.py
echo "__version__ = \"$VERSION\"" > app/version.py
echo "Wrote version to app/version.py"

BUILD_DIR="build_simple-timer-$VERSION"

rm -rf "$BUILD_DIR"
mkdir "$BUILD_DIR"

# Copy only app, device, features, main.py, requirements.txt (NO tests)
cp -r app device fonts features main.py requirements.txt "$BUILD_DIR"/


# Optionally: copy install.sh if you have one for Pi setup
cp install.sh "$BUILD_DIR/"
chmod +x "$BUILD_DIR/install.sh"

tar czf "$BUILD_DIR.tar.gz" "$BUILD_DIR"

rm -rf "$BUILD_DIR"

echo "Source packaging complete. Distributable: $BUILD_DIR.tar.gz"
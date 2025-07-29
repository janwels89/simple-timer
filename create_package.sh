#!/bin/bash
set -e

# Detect version from latest git tag
VERSION=$(git describe --tags --abbrev=0)
GIT_DESCRIBE=$(git describe --tags --always)

# If HEAD is not at the tag, append short hash
if [[ "$GIT_DESCRIBE" != "$VERSION" ]]; then
    SHORT_HASH=$(git rev-parse --short HEAD)
    VERSION="${VERSION}-${SHORT_HASH}"
fi

echo "Detected version: $VERSION"

# Inject version into app/version.py
echo "__version__ = \"$VERSION\"" > app/version.py
echo "Wrote version to app/version.py"

IMAGE_NAME="pyinstaller-arm64"
DOCKERFILE="Dockerfile.pyinstaller-arm64"
BUILD_DIR="build_arm64"
DEPLOY_DIR="simple-timer-$VERSION"

echo "Building Podman image $IMAGE_NAME ..."
podman build --platform linux/arm64 -f "$DOCKERFILE" -t "$IMAGE_NAME" .

rm -rf "$BUILD_DIR" "$DEPLOY_DIR" dist build __pycache__

mkdir "$BUILD_DIR"
cp -r app main.py requirements.txt "$BUILD_DIR"/

podman run --rm \
    -v "$PWD/build_arm64":/work:Z \
    -w /work \
    --user 0:0 \
    "$IMAGE_NAME" \
    bash -c "ls -l && pyinstaller --onefile main.py --name simple-timer"

mkdir "$DEPLOY_DIR"
cp "$BUILD_DIR/dist/simple-timer" "$DEPLOY_DIR/"

tar czf "$DEPLOY_DIR.tar.gz" "$DEPLOY_DIR"

rm -rf "$BUILD_DIR" "$DEPLOY_DIR"

echo "Build and packaging complete. Distributable: $DEPLOY_DIR.tar.gz"
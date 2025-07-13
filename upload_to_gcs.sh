#!/bin/bash
# ABOUTME: Script to upload supported code files to GCS bucket
# ABOUTME: Filters by extension and size, preserves directory structure

BUCKET_NAME="sankhya-gen-lang-client-0871164439"
GCS_FOLDER_PATH="sankhya"
LOCAL_REPO_PATH="./cloned_repo"
MAX_SIZE_BYTES=$((10 * 1024 * 1024))  # 10 MB

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting upload to GCS..."
echo "Bucket: gs://${BUCKET_NAME}/${GCS_FOLDER_PATH}/"

# Supported extensions
EXTENSIONS=(
    "\.py$" "\.java$" "\.js$" "\.ts$" "\.go$" "\.c$" "\.cpp$" "\.h$" "\.hpp$"
    "\.cs$" "\.rb$" "\.php$" "\.swift$" "\.kt$" "\.scala$"
    "\.md$" "\.txt$" "\.rst$" "\.html$" "\.css$" "\.scss$"
    "\.yaml$" "\.yml$" "\.json$" "\.xml$" "\.proto$" "\.sh$"
    "\.tf$" "\.tfvars$" "\.bicep$" "\.gradle$"
)

# Exact filename matches
EXACT_FILES=("Dockerfile" "pom.xml" "requirements.txt" "package.json" "go.mod" "go.sum" "Cargo.toml")

uploaded=0
skipped=0

# Function to check if file matches supported extensions
is_supported() {
    local file=$1
    local filename=$(basename "$file")
    
    # Check exact matches
    for exact in "${EXACT_FILES[@]}"; do
        if [[ "$filename" == "$exact" ]]; then
            return 0
        fi
    done
    
    # Check extensions
    for ext in "${EXTENSIONS[@]}"; do
        if [[ "$file" =~ $ext ]]; then
            return 0
        fi
    done
    
    return 1
}

# Find and upload files
while IFS= read -r -d '' file; do
    # Skip .git directory
    if [[ "$file" == *"/.git/"* ]]; then
        continue
    fi
    
    if is_supported "$file"; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        
        if [[ $size -gt $MAX_SIZE_BYTES ]]; then
            echo "  Skipping large file ($(($size / 1024 / 1024)) MB): $file"
            ((skipped++))
            continue
        fi
        
        # Calculate relative path
        rel_path=${file#$LOCAL_REPO_PATH/}
        gcs_path="gs://${BUCKET_NAME}/${GCS_FOLDER_PATH}/${rel_path}"
        
        # Upload file
        ~/google-cloud-sdk/bin/gsutil -q cp "$file" "$gcs_path"
        if [[ $? -eq 0 ]]; then
            ((uploaded++))
            if [[ $((uploaded % 50)) -eq 0 ]]; then
                echo "  Uploaded $uploaded files..."
            fi
        else
            echo "  Error uploading: $file"
        fi
    fi
done < <(find "$LOCAL_REPO_PATH" -type f -print0)

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Upload complete!"
echo "Total files uploaded: $uploaded"
echo "Total files skipped: $skipped"
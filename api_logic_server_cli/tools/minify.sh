#!/usr/bin/env bash
#
# Minify a project directory: copy the necessary files to a new directory
#
# $1: source project directory
# $2: target project directory
#

usage() {
    echo "Usage: $0 <source_project_directory> [target_project_directory]"
    echo "Minify a project directory: copy the necessary files to a new directory"
    echo
    echo "Arguments:"
    echo "  <source_project_directory>  The directory of the source project"
    echo "  [target_project_directory]  The directory where the minified project will be created (optional)"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

PROJECT_DIR=$(realpath "$1")
MINIFIED_PARENT_DIR=$(realpath "${2:-.}") # can be empty, in which case the minified project will be created in the current directory

if [[ ! -d "${PROJECT_DIR}" ]]; then
    echo "Invalid argument: source_project_directory: ${PROJECT_DIR} does not exist!" >&2
    exit 1
fi

if [[ ! -f "${PROJECT_DIR}/database/models.py" || ! -f "${PROJECT_DIR}/database/db.sqlite" ]]; then
    echo "Invalid project directory" >&2
    exit 1
fi

script_dir=$(dirname "$0")
minify_skel_dir="${script_dir}/mini_skel/"

if [[ ! -d "${minify_skel_dir}" ]]; then
    echo "Missing skeleton directory (${minify_skel_dir})" >&2
    exit 1
fi

project_name=$(basename "${PROJECT_DIR}")
minified_dir_name="${MINIFIED_PARENT_DIR}/${project_name}-mini"

if [[ -d "${minified_dir_name}" ]]; then
    echo "The target directory already exists: ${minified_dir_name}" >&2
    read -p "Do you want to continue and overwrite the existing directory? (y/n): " choice
    case "$choice" in 
      y|Y ) rm -rf "${minified_dir_name}";;
      n|N ) echo "Operation aborted."; exit 1;;
      * ) echo "Invalid choice. Operation aborted."; exit 1;;
    esac
fi

mkdir -p "${minified_dir_name}"
cd "${minified_dir_name}" || exit 1

cp -r "${minify_skel_dir}"/* .
cp "${PROJECT_DIR}/database/"{models.py,db.sqlite} database/
cp "${PROJECT_DIR}/ui/admin/admin.yaml" ui/admin/admin.yaml


echo "Created ${minified_dir_name}"
echo "You can now run the minified project with:"
echo "cd ${minified_dir_name}"
echo "python run.py"

#!/bin/bash

# Exit on error
set -e

# Compatibility matrix
declare -A compatibility_matrix=(
    # Format: "TensorFlow Version" -> "CUDA Version,cudNN Version,Python Version Range,Compiler,Build Tools"
    ["2.18.0"]="12.5,9.3,3.9-3.12,Clang 17.0.6,Bazel 6.5.0"
    ["2.17.0"]="12.3,8.9,3.9-3.12,Clang 17.0.6,Bazel 6.5.0"
    ["2.16.1"]="12.3,8.9,3.9-3.12,Clang 17.0.6,Bazel 6.5.0"
    ["2.15.0"]="12.2,8.9,3.9-3.11,Clang 16.0.0,Bazel 6.1.0"
    ["2.14.0"]="11.8,8.7,3.9-3.11,Clang 16.0.0,Bazel 6.1.0"
    ["2.13.0"]="11.8,8.6,3.8-3.11,Clang 16.0.0,Bazel 5.3.0"
    ["2.12.0"]="11.8,8.6,3.8-3.11,GCC 9.3.1,Bazel 5.3.0"
    ["2.11.0"]="11.2,8.1,3.7-3.10,GCC 9.3.1,Bazel 5.3.0"
    ["2.10.0"]="11.2,8.1,3.7-3.10,GCC 9.3.1,Bazel 5.1.1"
)

# Prompt for TensorFlow version
read -p "Enter TensorFlow version (e.g., 2.18.0): " tf_version

# Check if the TensorFlow version is supported
if [[ -z "${compatibility_matrix[$tf_version]}" ]]; then
    echo "Error: Unsupported TensorFlow version or not in the compatibility matrix."
    exit 1
fi

# Parse compatibility details
IFS=',' read -r cuda_version cudnn_version python_range compiler build_tools <<< "${compatibility_matrix[$tf_version]}"

# Display selected versions
echo "Installing TensorFlow $tf_version"
echo "CUDA Version: $cuda_version"
echo "cuDNN Version: $cudnn_version"
echo "Python Range: $python_range"
echo "Compiler: $compiler"
echo "Build Tools: $build_tools"

# Step 1: Install NVIDIA driver
echo "Installing NVIDIA driver..."
sudo apt update
sudo apt install -y nvidia-driver-535
sudo reboot

# Step 2: Add CUDA repository and install CUDA
echo "Installing CUDA $cuda_version..."
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$(lsb_release -sr | tr -d .)/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$(lsb_release -sr | tr -d .)/x86_64 /"
sudo apt update
sudo apt install -y cuda-${cuda_version//./-}

# Step 3: Install cuDNN
echo "Installing cuDNN $cudnn_version..."
cudnn_url="https://developer.download.nvidia.com/compute/cudnn/secure/${cudnn_version//./}/local_installers/cudnn-linux-x86_64-${cudnn_version}-cuda${cuda_version//./}.tgz"
wget --content-disposition --no-check-certificate "$cudnn_url"
tar -xvzf cudnn-linux-x86_64-${cudnn_version}-cuda${cuda_version//./}.tgz
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# Step 4: Install Python and TensorFlow
echo "Setting up Python environment..."
read -p "Enter Python version from $python_range (e.g., 3.10): " python_version
sudo apt install -y python${python_version} python${python_version}-venv python${python_version}-dev
python${python_version} -m venv tf_env
source tf_env/bin/activate
pip install --upgrade pip
pip install tensorflow==$tf_version

# Step 5: Set environment variables
echo "Setting environment variables..."
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Step 6: Verify Installation
echo "Verifying TensorFlow installation..."
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__); print('Num GPUs Available:', len(tf.config.list_physical_devices('GPU')))"

echo "Installation completed successfully!"

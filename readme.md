$python --version
python 3.12.11

$cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04 (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy
$nvidia-smi
Sun Sep 14 23:05:21 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.158.01             Driver Version: 570.158.01     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla V100-SXM2-32GB           On  |   00000000:00:08.0 Off |                  Off |
| N/A   60C    P0            183W /  300W |   31589MiB /  32768MiB |     88%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A          299381      C   python                                31574MiB |
+-----------------------------------------------------------------------------------------+
$ sudo dpkg -l |grep nvidia
ii  libnvidia-container-tools              1.13.5-1                                amd64        NVIDIA container runtime library (command-line tools)
ii  libnvidia-container1:amd64             1.13.5-1                                amd64        NVIDIA container runtime library
ii  nvidia-container-toolkit               1.13.5-1                                amd64        NVIDIA Container toolkit
ii  nvidia-container-toolkit-base          1.13.5-1                                amd64        NVIDIA Container Toolkit Base
ii  nvidia-docker2                         2.13.0-1                                all          nvidia-docker CLI wrapper

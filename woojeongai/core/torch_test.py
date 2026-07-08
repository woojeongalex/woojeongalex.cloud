import sys
import torch

print("Python :", sys.version.split()[0])
print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))
    x = torch.tensor([1.0, 2.0, 3.0]).cuda()
    y = x * 2
    print("Tensor on GPU:", y)
    print("GPU OK")
else:
    print("CUDA not available - CPU only")
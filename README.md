# Python Strategy Service - `friedman`

```powershell
# Generate the Python gRPC client and server stubs
Update-PythonGrpc -ProtosArray @("model", "strategy", "playing_field")

# Run the Friedman strategy service
# - The playing_field service has to be started first
python3 friedman_strategy.py
```

## Building the Project with Nix

To build the project using Nix, you can run the following command:

```sh
nix build
```

/*
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Author: Steffen70 <steffen@seventy.mx>
  Creation Date: 2024-07-25

  Contributors:
  - Contributor Name <contributor@example.com>
*/

{
  description = "A development environment for working with Python and gRPC.";

  inputs = {
    base_flake.url = "github:seventymx/game_theory_grpc_base_flake";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self, base_flake, ... }@inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        unstable = import inputs.nixpkgs { inherit system; };

        pname = "friedman-service";
        version = "${base_flake.majorMinorVersion.${system}}.0";

        baseDevShell = base_flake.devShell.${system};

        # Create a custom Python environment with the necessary packages
        myPython = unstable.python312.withPackages (
          ps: with ps; [
            grpcio
            grpcio-tools
            protobuf
          ]
        );

        dependencies = baseDevShell.buildInputs ++ [ myPython ];
      in
      {
        devShell = unstable.mkShell {
          buildInputs = dependencies;
          shellHook = baseDevShell.shellHook;
        };

        packages.default = unstable.stdenv.mkDerivation {
          pname = pname;
          version = version;

          src = ./.;

          buildInputs = dependencies;

          buildPhase = ''
            # Set environment variables for compilation
            export PROTOBUF_PATH=${base_flake.protos.${system}}

            export PSModulePath="${base_flake.powershell_modules.${system}}"

            pwsh -Command "& {
              Import-Module GrpcGenerator

              # Generate the gRPC client and server code from the protos
              Update-PythonGrpc -ProtosArray @('model', 'strategy', 'playing_field')
            }"

            # Copy all .py files to the output directory while preserving the directory structure
            rsync -av --include='*/' --include='*.py' --include='LICENSE' --exclude='*' . "$out"
          '';

          meta = with inputs.nixpkgs.lib; {
            description = "The main service of the Game Theory Demo Application.";
            license = licenses.mpl20;
            maintainers = with maintainers; [ steffen70 ];
          };
        };
      }
    );
}

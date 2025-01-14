"""This module is used for Nif file operations"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2025, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

from pyffi.formats.nif import NifFormat

import os
import os.path as path

import nifgen.formats.nif as NifFormat


class NifFile:
    """Class to load and save NIFs."""

    @staticmethod
    def load_nif(file_path):
        """Loads a NIF from the given file path."""
        NifLog.info(f"Importing {file_path}")

        file_ext = path.splitext(file_path)[1]

        # open file for binary reading
        with open(file_path, "rb") as nif_stream:
            # check if nif file is valid
            modification, (version, user_version, bs_version) = NifFormat.NifFile.inspect_version_only(nif_stream)
            if version >= 0:
                # it is valid, so read the file
                NifLog.info(f"NIF file version: {version:x}")
                NifLog.info(f"Reading {file_ext} file")
                nif_data = NifFormat.NifFile.from_stream(nif_stream)
            elif version == -1:
                raise NifError("Unsupported NIF version.")
            else:
                raise NifError("Not a NIF file.")

        return nif_data

    @staticmethod
    def save_nif(nif_data, file_path):
        """Saves a NIF at the given file path."""
        NifLog.info(f"Exporting {file_path}")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'wb') as out_file:
                nif_data.write(out_file)
        except Exception as e:
            raise NifError(str(e))
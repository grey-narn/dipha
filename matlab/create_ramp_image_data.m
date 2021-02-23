%  Copyright 2014 IST Austria
%
%  Contributed by: Jan Reininghaus
%
%  This file is part of DIPHA.
%
%  DIPHA is free software: you can redistribute it and/or modify
%  it under the terms of the GNU Lesser General Public License as published by
%  the Free Software Foundation, either version 3 of the License, or
%  (at your option) any later version.
%
%  DIPHA is distributed in the hope that it will be useful,
%  but WITHOUT ANY WARRANTY; without even the implied warranty of
%  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%  GNU Lesser General Public License for more details.
%
%  You should have received a copy of the GNU Lesser General Public License
%  along with DIPHA.  If not, see <http://www.gnu.org/licenses/>.

function create_ramp_image_data( dimension, resolution )
    %% create filename based on parameters
    filename = ['ramp_' num2str( dimension) '_' num2str( resolution ) '.complex'];

    %% create actual data
    lattice_resolution = repmat( resolution, 1, dimension );
    data = reshape( 1:prod( lattice_resolution ), lattice_resolution );

    %% save to disk in DIPHA format
    save_image_data( data, filename );
end
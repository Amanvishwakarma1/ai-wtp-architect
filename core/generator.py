import os
import numpy as np
import trimesh
from datetime import datetime
import re


class SimpleCADGenerator:

    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    # ============================================================
    # MAIN BUILD
    # ============================================================

    def build_3d_model(self, json_params, user_prompt=""):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scene = trimesh.Scene()

        mld = self.extract_mld(user_prompt)
        trains = self.train_count(mld)
        scale = max(1, mld / 80)

        rack_y = 250 * scale
        rack_height = 90 * scale

        main_pipe = 5 * scale
        branch_pipe = 3 * scale

        train_spacing = 400 * scale
        base_x = -((trains - 1) / 2) * train_spacing

        # ============================================================
        # GROUND
        # ============================================================

        ground = trimesh.creation.box(
            extents=[train_spacing * trains + 800 * scale,
                     1500 * scale,
                     20]
        )
        ground.visual.face_colors = [170, 170, 170, 255]
        ground.apply_translation([0, 0, -20])
        scene.add_geometry(ground)

        # ============================================================
        # MAIN HEADER
        # ============================================================

        header_start = base_x - 200 * scale
        header_end = base_x + train_spacing * (trains - 1)

        header = self.pipe(
            [header_start, rack_y, rack_height],
            [header_end, rack_y, rack_height],
            main_pipe
        )
        scene.add_geometry(header)

        # ============================================================
        # STORAGE TANK
        # ============================================================

        storage_x = header_end + 350 * scale
        storage_radius = 50 * scale
        storage_height = 80 * scale

        storage = self.tank(storage_x, 0, storage_radius, storage_height)
        scene.add_geometry(storage)

        train_outputs = []

        # ============================================================
        # TREATMENT TRAINS
        # ============================================================

        for i in range(trains):

            x = base_x + i * train_spacing

            mixer = self.tank(x, 0, 25 * scale, 60 * scale)
            clarifier = self.tank(x, -200 * scale, 40 * scale, 50 * scale)
            filter_block = self.block(x, -400 * scale,
                                      100 * scale,
                                      80 * scale,
                                      40 * scale)

            scene.add_geometry(mixer)
            scene.add_geometry(clarifier)
            scene.add_geometry(filter_block)

            nozzle_z = 45 * scale

            nozzle = self.professional_nozzle(x, 0, nozzle_z, branch_pipe)
            scene.add_geometry(nozzle)

            drop = self.pipe(
                [x, rack_y, rack_height],
                [x, rack_y - 100 * scale, rack_height],
                branch_pipe
            )
            scene.add_geometry(drop)

            elbow1 = self.elbow_90(
                [x, rack_y - 100 * scale, rack_height],
                branch_pipe,
                axis="z"
            )
            scene.add_geometry(elbow1)

            vertical = self.pipe(
                [x, rack_y - 100 * scale, rack_height],
                [x, rack_y - 100 * scale, nozzle_z],
                branch_pipe
            )
            scene.add_geometry(vertical)

            horizontal = self.pipe(
                [x, rack_y - 100 * scale, nozzle_z],
                [x, 0, nozzle_z],
                branch_pipe
            )
            scene.add_geometry(horizontal)

            pipe_mc = self.pipe(
                [x, 0, nozzle_z],
                [x, -200 * scale, 40 * scale],
                branch_pipe
            )
            scene.add_geometry(pipe_mc)

            pipe_cf = self.pipe(
                [x, -200 * scale, 40 * scale],
                [x, -400 * scale, 35 * scale],
                branch_pipe
            )
            scene.add_geometry(pipe_cf)

            train_outputs.append([x, -400 * scale, 35 * scale])

        # ============================================================
        # OUTPUT ROUTING (SAFE FOR SINGLE OR MULTI TRAIN)
        # ============================================================

        merge_y = -500 * scale

        if trains == 1:

            output = train_outputs[0]

            direct_drop = self.pipe(
                output,
                [output[0], merge_y, output[2]],
                branch_pipe
            )
            scene.add_geometry(direct_drop)

            self.route_to_storage(scene,
                                  output[0],
                                  merge_y,
                                  35 * scale,
                                  storage_x,
                                  storage_radius,
                                  branch_pipe,
                                  scale)

        else:

            for output in train_outputs:
                merge_pipe = self.pipe(
                    output,
                    [output[0], merge_y, output[2]],
                    branch_pipe
                )
                scene.add_geometry(merge_pipe)

            merge_header = self.pipe(
                [base_x, merge_y, 35 * scale],
                [base_x + train_spacing * (trains - 1),
                 merge_y,
                 35 * scale],
                branch_pipe
            )
            scene.add_geometry(merge_header)

            drop_x = base_x + train_spacing * (trains - 1)

            self.route_to_storage(scene,
                                  drop_x,
                                  merge_y,
                                  35 * scale,
                                  storage_x,
                                  storage_radius,
                                  branch_pipe,
                                  scale)

        # ============================================================
        # CENTER & EXPORT
        # ============================================================

        scene = self.center(scene)

        glb_path = os.path.join(self.export_dir, f"wtp_{timestamp}.glb")
        scene.export(glb_path)

        combined = trimesh.util.concatenate(scene.dump())
        stl_path = os.path.join(self.export_dir, f"wtp_{timestamp}.stl")
        combined.export(stl_path)

        return glb_path, stl_path

    # ============================================================
    # STORAGE ROUTING (PROFESSIONAL CONNECTION)
    # ============================================================

    def route_to_storage(self, scene,
                         drop_x,
                         merge_y,
                         drop_z,
                         storage_x,
                         storage_radius,
                         radius,
                         scale):

        vertical_rise = self.pipe(
            [drop_x, merge_y, drop_z],
            [drop_x, merge_y, 90 * scale],
            radius
        )
        scene.add_geometry(vertical_rise)

        elbow_turn = self.elbow_90(
            [drop_x, merge_y, 90 * scale],
            radius,
            axis="y"
        )
        scene.add_geometry(elbow_turn)

        horizontal_run = self.pipe(
            [drop_x, merge_y, 90 * scale],
            [storage_x - storage_radius - 20 * scale,
             0,
             90 * scale],
            radius
        )
        scene.add_geometry(horizontal_run)

        elbow_down = self.elbow_90(
            [storage_x - storage_radius - 20 * scale,
             0,
             90 * scale],
            radius,
            axis="z"
        )
        scene.add_geometry(elbow_down)

        final_drop = self.pipe(
            [storage_x - storage_radius - 20 * scale,
             0,
             90 * scale],
            [storage_x - storage_radius,
             0,
             60 * scale],
            radius
        )
        scene.add_geometry(final_drop)

        storage_nozzle = self.professional_nozzle(
            storage_x - storage_radius,
            0,
            60 * scale,
            radius
        )
        scene.add_geometry(storage_nozzle)

    # ============================================================
    # COMPONENT HELPERS
    # ============================================================

    def professional_nozzle(self, x, y, z, radius):

        stub = trimesh.creation.cylinder(
            radius=radius * 1.05,
            height=radius * 3,
            sections=32
        )

        flange = trimesh.creation.cylinder(
            radius=radius * 1.8,
            height=radius * 0.6,
            sections=32
        )
        flange.apply_translation([0, 0, radius * 3])

        neck = trimesh.creation.cylinder(
            radius=radius * 1.3,
            height=radius,
            sections=32
        )
        neck.apply_translation([0, 0, radius * 2])

        nozzle = trimesh.util.concatenate([stub, neck, flange])
        nozzle.visual.face_colors = [130, 130, 130, 255]
        nozzle.apply_translation([x, y, z])
        return nozzle

    def elbow_90(self, position, radius, axis="y"):

        elbow = trimesh.creation.torus(
            major_radius=radius * 2.5,
            minor_radius=radius,
            major_sections=32,
            minor_sections=16
        )

        elbow.visual.face_colors = [100, 100, 100, 255]

        if axis == "y":
            elbow.apply_transform(
                trimesh.transformations.rotation_matrix(
                    np.pi / 2,
                    [0, 1, 0]
                )
            )

        if axis == "z":
            elbow.apply_transform(
                trimesh.transformations.rotation_matrix(
                    np.pi / 2,
                    [0, 0, 1]
                )
            )

        elbow.apply_translation(position)
        return elbow

    def tank(self, x, y, radius, height):
        body = trimesh.creation.cylinder(radius=radius,
                                         height=height,
                                         sections=64)
        body.apply_translation([0, 0, height / 2])

        dome = trimesh.creation.icosphere(subdivisions=2,
                                          radius=radius)
        dome.vertices[:, 2] = np.maximum(dome.vertices[:, 2], 0)
        dome.apply_translation([0, 0, height])

        tank = trimesh.util.concatenate([body, dome])
        tank.visual.face_colors = [210, 210, 210, 255]
        tank.apply_translation([x, y, 0])
        return tank

    def block(self, x, y, w, d, h):
        b = trimesh.creation.box(extents=[w, d, h])
        b.visual.face_colors = [200, 200, 200, 255]
        b.apply_translation([x, y, h / 2])
        return b

    def pipe(self, start, end, radius):
        start = np.array(start)
        end = np.array(end)
        direction = end - start
        length = np.linalg.norm(direction)

        if length < 1e-6:
            return None

        cyl = trimesh.creation.cylinder(radius=radius,
                                        height=length,
                                        sections=32)
        cyl.apply_translation([0, 0, length / 2])

        rot = trimesh.geometry.align_vectors(
            [0, 0, 1],
            direction / length
        )
        cyl.apply_transform(rot)
        cyl.apply_translation(start)
        cyl.visual.face_colors = [100, 100, 100, 255]
        return cyl

    def center(self, scene):
        combined = trimesh.util.concatenate(scene.dump())
        centroid = combined.centroid
        transform = np.eye(4)
        transform[:3, 3] = -centroid
        scene.apply_transform(transform)
        return scene

    def extract_mld(self, prompt):
        match = re.search(r'(\d+)\s*MLD', prompt, re.IGNORECASE)
        return int(match.group(1)) if match else 100

    def train_count(self, mld):
        if mld <= 50:
            return 1
        elif mld <= 150:
            return 2
        elif mld <= 300:
            return 3
        else:
            return 4


_generator = SimpleCADGenerator()
build_3d_model = _generator.build_3d_model

import tkinter as tk
from tkinter import filedialog, messagebox
import pyfbx


class FBXCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FBX Cleaner")

        # Add a button to load the FBX file
        self.load_button = tk.Button(root, text="Load FBX File", command=self.load_fbx)
        self.load_button.pack()

        # Add checkboxes for various cleaning options
        self.clean_mesh_var = tk.BooleanVar()
        self.clean_material_var = tk.BooleanVar()
        self.clean_animation_var = tk.BooleanVar()

        tk.Checkbutton(root, text="Clean Mesh Data", variable=self.clean_mesh_var).pack()
        tk.Checkbutton(root, text="Clean Material Data", variable=self.clean_material_var).pack()
        tk.Checkbutton(root, text="Clean Animation Data", variable=self.clean_animation_var).pack()

        # Add a button to perform the cleaning
        self.clean_button = tk.Button(root, text="Clean FBX File", command=self.clean_fbx)
        self.clean_button.pack()

        self.fbx_file_path = None

    def load_fbx(self):
        self.fbx_file_path = filedialog.askopenfilename(filetypes=[("FBX files", "*.fbx")])
        if not self.fbx_file_path:
            messagebox.showwarning("Warning", "No FBX file selected!")

    def clean_fbx(self):
        if not self.fbx_file_path:
            messagebox.showwarning("Warning", "No FBX file loaded!")
            return

        try:
            # Initialize FBX Manager and Scene
            manager = pyfbx.FbxManager.Create()
            importer = pyfbx.FbxImporter.Create(manager, "")
            scene = pyfbx.FbxScene.Create(manager, "Scene")

            success = importer.Initialize(self.fbx_file_path, -1, manager.GetIOSettings())
            if not success:
                raise RuntimeError(f"Failed to initialize importer: {importer.GetStatus().GetErrorString()}")

            success = importer.Import(scene)
            importer.Destroy()
            if not success:
                raise RuntimeError("Failed to import FBX file")

            # Perform cleaning based on user selection
            if self.clean_mesh_var.get():
                self.clean_mesh_data(scene)
            if self.clean_material_var.get():
                self.clean_material_data(scene)
            if self.clean_animation_var.get():
                self.clean_animation_data(scene)

            # Save the cleaned FBX file
            save_path = filedialog.asksaveasfilename(defaultextension=".fbx",
                                                     filetypes=[("FBX files", "*.fbx")])
            if save_path:
                exporter = pyfbx.FbxExporter.Create(manager, "")
                success = exporter.Initialize(save_path, -1, manager.GetIOSettings())
                if not success:
                    raise RuntimeError(f"Failed to initialize exporter: {exporter.GetStatus().GetErrorString()}")

                success = exporter.Export(scene)
                exporter.Destroy()
                if not success:
                    raise RuntimeError("Failed to export FBX file")

                messagebox.showinfo("Info", "FBX file cleaned and saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process FBX file: {e}")

    def clean_mesh_data(self, scene):
        # Example of removing all mesh nodes
        root_node = scene.GetRootNode()
        to_remove = []
        for i in range(root_node.GetChildCount()):
            child = root_node.GetChild(i)
            if child.GetNodeAttribute() and child.GetNodeAttribute().GetAttributeType() == pyfbx.FbxNodeAttribute.eMesh:
                to_remove.append(child)
                print(f"Marked mesh for removal: {child.GetName()}")

        for mesh in to_remove:
            root_node.RemoveChild(mesh)
            print(f"Removed mesh: {mesh.GetName()}")

    def clean_material_data(self, scene):
        # Example of removing all material nodes
        materials = [scene.GetMaterial(i) for i in range(scene.GetMaterialCount())]
        for material in materials:
            scene.RemoveMaterial(material)
            print(f"Removed material: {material.GetName()}")

    def clean_animation_data(self, scene):
        # Example of removing all animation stacks
        anim_stacks = [scene.GetSrcObject(pyfbx.FbxCriteria.ObjectType(pyfbx.FbxAnimStack), i)
                       for i in range(scene.GetSrcObjectCount(pyfbx.FbxCriteria.ObjectType(pyfbx.FbxAnimStack)))]
        for anim_stack in anim_stacks:
            scene.RemoveSrcObject(anim_stack)
            print(f"Removed animation stack: {anim_stack.GetName()}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FBXCleanerApp(root)
    root.mainloop()

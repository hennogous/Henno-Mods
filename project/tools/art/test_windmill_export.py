"""Regression: a legacy GEO parsed for rendering must remain loadable by Firaxis."""
import tempfile,unittest
from pathlib import Path
from windmill_tower_integrate import read_xml,save,validate_native_groups

class GeometryTypeRegression(unittest.TestCase):
    def test_unused_native_group_cannot_be_silently_omitted_from_geo(self):
        mesh=dict(name='Sails',materialBindingNames=['Plaster','Sails'],triangles=[[0,1,2,1]],groups=[dict(count=0),dict(count=1)])
        with self.assertRaises(ValueError):validate_native_groups(mesh)
        mesh.update(materialBindingNames=['Sails'],triangles=[[0,1,2,0]],groups=[dict(count=1)])
        validate_native_groups(mesh)

    def test_legacy_geo_is_written_with_registered_native_type(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'legacy.geo';target=Path(d)/'new.geo'
            source.write_text('<AssetObjects:GeometryInstance><m_Name text="Tower"/><m_Meshes/></AssetObjects:GeometryInstance>')
            root=read_xml(source)
            self.assertEqual(root.tag,'AssetObjects.GeometryInstance')
            save(root,target)
            actual=read_xml(target)
            self.assertEqual(actual.tag,'AssetObjects..GeometryInstance')
            self.assertEqual(actual.find('m_Name').get('text'),'Tower')
            self.assertIsNotNone(actual.find('m_Meshes'))
            before=target.read_bytes();save(actual,target)
            self.assertEqual(before,target.read_bytes())

if __name__=='__main__':unittest.main()

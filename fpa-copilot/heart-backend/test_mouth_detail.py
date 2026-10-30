import unittest
import numpy as np
from mouth_detail import blend_mouth


class DetailTests(unittest.TestCase):
    def frames(self):
        source=np.full((200,200,3),100,dtype=np.uint8)
        generated=source.copy();generated[85:116,75:126]=180
        t=np.arange(20)*np.pi/10
        lips=np.stack((100+20*np.cos(t),100+10*np.sin(t)),axis=1)
        return source,generated,lips

    def test_preserves_pixels_outside_support_without_mutating_inputs(self):
        source,generated,lips=self.frames();a=source.copy();b=generated.copy()
        result,alpha=blend_mouth(source,generated,lips,lips+np.array([0,3]))
        np.testing.assert_array_equal(source,a);np.testing.assert_array_equal(generated,b)
        np.testing.assert_array_equal(result[alpha==0],source[alpha==0])
        self.assertTrue((alpha==1).any());self.assertTrue(((alpha>0)&(alpha<1)).any())
        self.assertTrue((result[alpha>0]!=source[alpha>0]).any())
        self.assertTrue(np.all(alpha[:60]==0))

    def test_rejects_invalid_contours_and_mismatched_frames(self):
        source,generated,lips=self.frames()
        for bad in (lips[:19],lips*np.nan,lips-500,lips*10):
            with self.subTest(shape=bad.shape),self.assertRaises(ValueError):
                blend_mouth(source,generated,lips,bad)
        with self.assertRaises(ValueError):blend_mouth(source,generated[:100],lips,lips)

    def test_identical_input_remains_identical(self):
        source,_,lips=self.frames()
        result,_=blend_mouth(source,source,lips,lips)
        np.testing.assert_array_equal(result,source)


if __name__=='__main__':unittest.main()

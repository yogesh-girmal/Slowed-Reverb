import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
import numpy as np

# Import the module to test
import gifslowed

class TestGifSlowed(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_audio_file = os.path.join(self.test_dir, "test_audio.mp3")
        self.test_output_file = os.path.join(self.test_dir, "test_output.mp3")
        self.test_gif_file = os.path.join(self.test_dir, "test.gif")
        self.test_video_output = os.path.join(self.test_dir, "test_output.mp4")
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('gifslowed.AudioSegment.from_file')
    @patch('gifslowed.np.array')
    @patch('gifslowed.Chorus')
    @patch('gifslowed.Reverb')
    def test_add_reverb_to_audio(self, mock_reverb, mock_chorus, mock_np_array, mock_audio_from_file):
        """Test the add_reverb_to_audio function."""
        # Mock AudioSegment objects
        mock_audio = MagicMock()
        mock_vinyl = MagicMock()
        mock_audio_with_vinyl = MagicMock()
        mock_slow_audio = MagicMock()
        
        mock_audio_from_file.side_effect = [mock_audio, mock_vinyl]
        mock_audio.overlay.return_value = mock_audio_with_vinyl
        mock_audio_with_vinyl._spawn.return_value = mock_slow_audio
        mock_slow_audio.frame_rate = 44100
        mock_slow_audio.get_array_of_samples.return_value = [1, 2, 3, 4]
        
        # Mock numpy array and effects
        mock_np_array.return_value = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        mock_chorus_instance = MagicMock()
        mock_reverb_instance = MagicMock()
        mock_chorus.return_value = mock_chorus_instance
        mock_reverb.return_value = mock_reverb_instance
        
        mock_chorus_instance.return_value = np.array([0.15, 0.25, 0.35, 0.45])
        mock_reverb_instance.return_value = np.array([0.2, 0.3, 0.4, 0.5])
        
        # Call the function
        gifslowed.add_reverb_to_audio(self.test_audio_file, self.test_output_file)
        
        # Assertions
        mock_audio_from_file.assert_any_call(self.test_audio_file)
        mock_audio_from_file.assert_any_call(gifslowed.vinyl)
        mock_audio.overlay.assert_called_once_with(mock_vinyl, loop=True)
        mock_slow_audio.export.assert_called_once_with(self.test_output_file, format='mp3')
    
    @patch('gifslowed.AudioFileClip')
    @patch('gifslowed.VideoFileClip')
    @patch('gifslowed.concatenate_videoclips')
    def test_merge_audio_gif(self, mock_concatenate, mock_video_clip, mock_audio_clip):
        """Test the merge_audio_gif function."""
        # Mock objects
        mock_audio = MagicMock()
        mock_gif = MagicMock()
        mock_video = MagicMock()
        
        mock_audio_clip.return_value = mock_audio
        mock_video_clip.return_value = mock_gif
        mock_concatenate.return_value = mock_video
        
        # Set up duration properties
        mock_audio.duration = 100
        mock_gif.duration = 10
        mock_video.set_audio.return_value = mock_video
        
        # Call the function
        gifslowed.merge_audio_gif(self.test_audio_file, self.test_gif_file, self.test_video_output)
        
        # Assertions
        mock_audio_clip.assert_called_once_with(self.test_audio_file)
        mock_video_clip.assert_called_once_with(self.test_gif_file)
        mock_video.set_audio.assert_called_once_with(mock_audio)
        mock_video.write_videofile.assert_called_once_with(self.test_video_output, verbose=False, logger=None)
    
    @patch('os.makedirs')
    def test_create_folders(self, mock_makedirs):
        """Test the create_folders function."""
        gifslowed.create_folders()
        
        # Check that makedirs was called for both folders
        expected_calls = [
            call(gifslowed.temp_video_folder, exist_ok=True),
            call(gifslowed.final_video_folder, exist_ok=True)
        ]
        mock_makedirs.assert_has_calls(expected_calls)
    
    @patch('time.sleep')
    @patch('shutil.rmtree')
    def test_delete_temp_audio_video(self, mock_rmtree, mock_sleep):
        """Test the delete_temp_audio_video function."""
        gifslowed.delete_temp_audio_video()
        
        # Check that sleep was called
        mock_sleep.assert_called_once_with(1)
        # Note: rmtree calls are commented out in the original code
    
    @patch('os.listdir')
    @patch('gifslowed.add_reverb_to_audio')
    @patch('gifslowed.merge_audio_gif')
    @patch('gifslowed.create_folders')
    @patch('gifslowed.delete_temp_audio_video')
    @patch('random.choice')
    def test_main_workflow_integration(self, mock_choice, mock_delete, mock_create, 
                                     mock_merge, mock_add_reverb, mock_listdir):
        """Test the main workflow integration."""
        # Mock file listings
        mock_listdir.side_effect = [
            ['song1.mp3', 'song2.mp3'],  # audio_files
            ['gif1.gif', 'gif2.gif']     # gif_files
        ]
        mock_choice.side_effect = ['gif1.gif', 'gif2.gif']
        
        # Mock the main workflow by importing and running the relevant parts
        # This would need to be refactored in the actual code to be more testable
        
        # Verify that the mocked functions would be called
        self.assertTrue(mock_listdir.called)
    
    def test_folder_constants(self):
        """Test that folder constants are properly defined."""
        self.assertEqual(gifslowed.audio_folder, "audio_folder")
        self.assertEqual(gifslowed.vinyl, "vinyl/vinyl.mp3")
        self.assertEqual(gifslowed.gif, "gif")
        self.assertEqual(gifslowed.temp_audio_folder, "temp_audio_folder")
        self.assertEqual(gifslowed.temp_video_folder, "temp_video_folder")
        self.assertEqual(gifslowed.final_video_folder, "final_video_folder")
        self.assertEqual(gifslowed.test, "test")
    
    @patch('gifslowed.AudioSegment.from_file')
    def test_add_reverb_to_audio_file_not_found(self, mock_audio_from_file):
        """Test add_reverb_to_audio with file not found."""
        mock_audio_from_file.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(FileNotFoundError):
            gifslowed.add_reverb_to_audio("nonexistent.mp3", self.test_output_file)
    
    @patch('gifslowed.VideoFileClip')
    def test_merge_audio_gif_invalid_gif(self, mock_video_clip):
        """Test merge_audio_gif with invalid GIF file."""
        mock_video_clip.side_effect = Exception("Invalid video file")
        
        with self.assertRaises(Exception):
            gifslowed.merge_audio_gif(self.test_audio_file, "invalid.gif", self.test_video_output)

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGifSlowed)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("All tests passed!")
    else:
        print("Some tests failed.")

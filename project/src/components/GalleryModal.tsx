import React, { useState } from 'react';
import { X, ImageIcon, Upload, Camera, Trash2, Download } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';

interface GalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface GalleryImage {
  id: string;
  url: string;
  name: string;
  uploadDate: Date;
  type: 'crop' | 'disease' | 'soil' | 'other';
}

const GalleryModal: React.FC<GalleryModalProps> = ({ isOpen, onClose }) => {
  const { language } = useAppContext();
  const [selectedTab, setSelectedTab] = useState<'all' | 'crop' | 'disease' | 'soil' | 'other'>('all');
  const [galleryImages, setGalleryImages] = useState<GalleryImage[]>([
    {
      id: '1',
      url: 'https://images.pexels.com/photos/1595104/pexels-photo-1595104.jpeg?auto=compress&cs=tinysrgb&w=400',
      name: 'Wheat Field Analysis',
      uploadDate: new Date('2024-01-15'),
      type: 'crop'
    },
    {
      id: '2',
      url: 'https://images.pexels.com/photos/1459505/pexels-photo-1459505.jpeg?auto=compress&cs=tinysrgb&w=400',
      name: 'Corn Disease Detection',
      uploadDate: new Date('2024-01-14'),
      type: 'disease'
    },
    {
      id: '3',
      url: 'https://images.pexels.com/photos/1595108/pexels-photo-1595108.jpeg?auto=compress&cs=tinysrgb&w=400',
      name: 'Soil Quality Test',
      uploadDate: new Date('2024-01-13'),
      type: 'soil'
    },
    {
      id: '4',
      url: 'https://images.pexels.com/photos/1595385/pexels-photo-1595385.jpeg?auto=compress&cs=tinysrgb&w=400',
      name: 'Rice Paddy Monitoring',
      uploadDate: new Date('2024-01-12'),
      type: 'crop'
    }
  ]);

  if (!isOpen) return null;

  const tabs = [
    { id: 'all', label: 'All Images', icon: ImageIcon },
    { id: 'crop', label: 'Crops', icon: Camera },
    { id: 'disease', label: 'Diseases', icon: Camera },
    { id: 'soil', label: 'Soil', icon: Camera },
    { id: 'other', label: 'Other', icon: Camera }
  ];

  const filteredImages = selectedTab === 'all' 
    ? galleryImages 
    : galleryImages.filter(img => img.type === selectedTab);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const newImage: GalleryImage = {
            id: Date.now().toString() + Math.random(),
            url: e.target?.result as string,
            name: file.name,
            uploadDate: new Date(),
            type: 'other'
          };
          setGalleryImages(prev => [newImage, ...prev]);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const deleteImage = (imageId: string) => {
    setGalleryImages(prev => prev.filter(img => img.id !== imageId));
  };

  const downloadImage = (imageUrl: string, imageName: string) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = imageName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat(language === 'hi' ? 'hi-IN' : 'en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 w-full max-w-6xl max-h-[90vh] m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ImageIcon className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-800">Image Gallery</h2>
          </div>
          <div className="flex items-center space-x-3">
            <label className="flex items-center space-x-2 bg-green-100 text-green-700 px-4 py-2 rounded-xl hover:bg-green-200 transition-colors cursor-pointer">
              <Upload className="w-4 h-4" />
              <span className="text-sm font-medium">Upload</span>
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </label>
            <button
              onClick={onClose}
              className="p-2 rounded-xl hover:bg-gray-100/80 transition-colors"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 p-6 pb-0">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-colors ${
                  selectedTab === tab.id
                    ? 'bg-green-100 text-green-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {filteredImages.length === 0 ? (
            <div className="text-center py-12">
              <ImageIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500 text-lg">No images in this category</p>
              <p className="text-gray-400 text-sm mt-2">Upload some images to get started</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredImages.map((image) => (
                <div
                  key={image.id}
                  className="bg-white/60 rounded-xl overflow-hidden border border-white/40 hover:shadow-lg transition-all duration-200 group"
                >
                  <div className="relative">
                    <img
                      src={image.url}
                      alt={image.name}
                      className="w-full h-32 object-cover"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => downloadImage(image.url, image.name)}
                          className="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
                        >
                          <Download className="w-4 h-4 text-gray-700" />
                        </button>
                        <button
                          onClick={() => deleteImage(image.id)}
                          className="p-2 bg-white/90 rounded-lg hover:bg-white transition-colors"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="p-3">
                    <h3 className="font-medium text-gray-800 text-sm truncate">
                      {image.name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(image.uploadDate)}
                    </p>
                    <div className="mt-2">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        image.type === 'crop' ? 'bg-green-100 text-green-700' :
                        image.type === 'disease' ? 'bg-red-100 text-red-700' :
                        image.type === 'soil' ? 'bg-amber-100 text-amber-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {image.type.charAt(0).toUpperCase() + image.type.slice(1)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GalleryModal;
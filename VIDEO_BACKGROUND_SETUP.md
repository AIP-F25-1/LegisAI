# Video Background Setup Guide

**Date**: December 2024  
**Status**: ✅ **IMPLEMENTED**

---

## ✅ IMPLEMENTATION COMPLETE

The slow-motion law-related background video feature has been implemented!

---

## 📁 FILES CREATED/MODIFIED

### New Files:
1. ✅ `frontend/src/components/VideoBackground.tsx` - Video background component
2. ✅ `frontend/public/videos/README.md` - Instructions for video setup

### Modified Files:
1. ✅ `frontend/src/App.tsx` - Added VideoBackground component
2. ✅ `frontend/src/index.css` - Updated body styles
3. ✅ `frontend/src/components/Layout.tsx` - Added z-index for content layering

---

## 🎬 HOW IT WORKS

### Video Background Component:
- **Location**: Fixed position, full viewport
- **Playback**: Auto-play, loop, muted
- **Effect**: Slow zoom animation (20s cycle)
- **Filter**: Brightness reduced, contrast/saturation enhanced
- **Overlay**: Gradient overlays for text readability
- **Fallback**: Gradient background if video not found

### Features:
- ✅ Slow-motion zoom effect (20-second cycle)
- ✅ Automatic looping
- ✅ Muted playback (no sound)
- ✅ Error handling (falls back to gradient)
- ✅ Text readability overlay
- ✅ Smooth animations

---

## 📥 ADDING YOUR VIDEO

### Step 1: Get a Law-Related Video

**Recommended Sources** (Free):
1. **Pexels**: https://www.pexels.com/search/videos/law/
   - Search: "law", "courtroom", "legal", "justice", "gavel"
   - Download: HD quality, MP4 format

2. **Pixabay**: https://pixabay.com/videos/search/law/
   - Search: "law", "court", "legal", "justice"
   - Filter: Free for commercial use

3. **Coverr**: https://coverr.co/
   - Search: "law", "legal", "court", "justice"

### Step 2: Process Video (Optional - for slow motion)

If you want to add slow-motion effect to the video itself:

1. **Using DaVinci Resolve** (Free):
   - Import video
   - Right-click clip → "Change Clip Speed"
   - Set to 50-70% speed
   - Export as MP4 (H.264)

2. **Using Online Tools**:
   - https://www.kapwing.com/tools/slow-motion
   - Upload video
   - Set speed to 0.5x or 0.7x
   - Download

### Step 3: Place Video

1. Create directory (if it doesn't exist):
   ```bash
   mkdir -p frontend/public/videos
   ```

2. Place video file:
   - **Filename**: `law-background.mp4`
   - **Location**: `frontend/public/videos/law-background.mp4`

### Step 4: Optimize Video (Recommended)

For best performance:
- **Resolution**: 1920x1080 (Full HD)
- **File Size**: Under 10MB
- **Duration**: 10-30 seconds (will loop)
- **Format**: MP4 (H.264 codec)
- **Frame Rate**: 24-30 fps

**Tools for optimization**:
- HandBrake (free): https://handbrake.fr/
- FFmpeg: `ffmpeg -i input.mp4 -vf scale=1920:1080 -crf 23 output.mp4`

---

## 🎨 CUSTOMIZATION

### Change Video Source:
Edit `frontend/src/components/VideoBackground.tsx`:
```tsx
<VideoBackground videoSrc="/videos/your-video.mp4" />
```

### Adjust Video Effects:
Edit the video style in `VideoBackground.tsx`:
```tsx
style={{
  filter: 'brightness(0.4) contrast(1.1) saturate(1.2)', // Adjust brightness/contrast
  transform: 'scale(1.1)', // Initial zoom level
  transition: 'transform 20s ease-in-out' // Animation speed
}}
```

### Adjust Overlay Opacity:
Edit overlay divs in `VideoBackground.tsx`:
```tsx
// Main overlay
<div className="absolute inset-0 bg-gradient-to-br from-purple-900/60 ..." />
// Change /60 to /40 for lighter overlay, /80 for darker

// Animated overlay
<div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 ..." />
```

### Change Animation Speed:
Edit CSS animation in `VideoBackground.tsx`:
```css
@keyframes slowZoom {
  0% { transform: scale(1.1); }
  100% { transform: scale(1.15); }
}
// Change 20s to 30s for slower, 10s for faster
```

---

## 🎯 RECOMMENDED VIDEO CONTENT

### Best Suited Scenes:
1. **Courtroom**: Empty courtroom, judge's bench, jury box
2. **Legal Documents**: Slow pan over legal documents, contracts
3. **Law Library**: Bookshelves, reading areas
4. **Abstract**: Scales of justice, gavel, legal symbols
5. **Professional**: Lawyer working, legal consultation
6. **Architecture**: Law firm buildings, courthouses

### Video Style:
- **Slow motion**: 50-70% speed
- **Smooth camera movement**: Pan, tilt, or dolly
- **Shallow depth of field**: Blurred background
- **Professional lighting**: Well-lit, cinematic
- **Color grading**: Cool tones (blues, purples) match theme

---

## ✅ CURRENT STATUS

- ✅ Video background component created
- ✅ Integrated into App.tsx
- ✅ Slow-motion zoom animation
- ✅ Overlay for text readability
- ✅ Error handling with fallback
- ✅ Z-index layering configured
- ⏳ **Waiting for video file**: Place `law-background.mp4` in `frontend/public/videos/`

---

## 🚀 TESTING

1. **Without Video** (Current):
   - App will show gradient fallback
   - All functionality works normally

2. **With Video**:
   - Place video in `frontend/public/videos/law-background.mp4`
   - Refresh browser
   - Video should auto-play, loop, and zoom slowly

---

## 📝 NOTES

- Video is **muted by default** (no sound)
- Video **loops automatically**
- **Slow zoom animation** adds depth
- **Overlay ensures text readability**
- **Fallback gradient** if video fails to load
- Video is **optimized for performance**

---

**The video background is ready! Just add your video file!** 🎬


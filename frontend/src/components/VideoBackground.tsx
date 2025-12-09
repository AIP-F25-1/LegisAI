import React, { useState, useRef, useEffect } from 'react'

interface VideoBackgroundProps {
  videoSrc?: string
  fallbackImage?: string
}

const VideoBackground: React.FC<VideoBackgroundProps> = ({ 
  videoSrc = '/videos/law-background.mp4',
  fallbackImage = '/images/law-background.jpg'
}) => {
  const [videoError, setVideoError] = useState(false)
  const [videoLoaded, setVideoLoaded] = useState(false)
  const reverseIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    // Try to load the video
    if (videoRef.current) {
      const video = videoRef.current
      
      const handleCanPlay = () => {
        setVideoLoaded(true)
        setVideoError(false)
        // Start playing forward slowly
        video.playbackRate = 0.5 // Slow motion (50% speed)
        video.play().catch(err => {
          console.log('Video play error:', err)
          setVideoError(true)
        })
      }
      
      const handleError = () => {
        console.log('Video load error - showing fallback')
        setVideoError(true)
        setVideoLoaded(false)
      }
      
      // Handle video end - play in reverse smoothly
      const handleEnded = () => {
        // Clear any existing reverse interval
        if (reverseIntervalRef.current) {
          clearInterval(reverseIntervalRef.current)
        }
        
        // Start reversing the video
        reverseIntervalRef.current = setInterval(() => {
          if (video.currentTime > 0.1) {
            // Seek backwards smoothly
            video.currentTime = Math.max(0, video.currentTime - 0.1)
          } else {
            // Reached the beginning, clear interval and play forward
            if (reverseIntervalRef.current) {
              clearInterval(reverseIntervalRef.current)
              reverseIntervalRef.current = null
            }
            video.currentTime = 0
            video.play() // Play forward again
          }
        }, 100) // Update every 100ms for smooth reverse
      }
      
      video.addEventListener('canplay', handleCanPlay)
      video.addEventListener('error', handleError)
      video.addEventListener('ended', handleEnded)
      
      // Try to load
      video.load()
      
      return () => {
        // Cleanup: clear interval and remove event listeners
        if (reverseIntervalRef.current) {
          clearInterval(reverseIntervalRef.current)
          reverseIntervalRef.current = null
        }
        video.removeEventListener('canplay', handleCanPlay)
        video.removeEventListener('error', handleError)
        video.removeEventListener('ended', handleEnded)
      }
    }
  }, [videoSrc])

  return (
    <div className="fixed inset-0 w-full h-full z-0 overflow-hidden">
      {/* Video Background */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        preload="auto"
        className={`absolute inset-0 w-full h-full object-cover video-bg ${videoLoaded && !videoError ? 'opacity-100' : 'opacity-0'}`}
        style={{
          filter: 'brightness(0.3) contrast(1.2) saturate(1.3)',
          transform: 'scale(1.1)',
          transition: 'opacity 1s ease-in-out, transform 20s ease-in-out',
          zIndex: 1,
          playbackRate: 0.5 // Slow motion (50% speed)
        }}
      >
        <source src={videoSrc} type="video/mp4" />
      </video>
      
      {/* Fallback gradient - only show if video fails */}
      {videoError && (
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        />
      )}
      
      {/* Dark base overlay for better text readability */}
      <div className="absolute inset-0 bg-black/70 transition-opacity duration-1000" />
      
      {/* Overlay for better text readability - darker when video is loaded */}
      <div className={`absolute inset-0 bg-gradient-to-br from-purple-900/80 via-blue-900/80 to-indigo-900/80 transition-opacity duration-1000 ${videoLoaded && !videoError ? 'opacity-70' : 'opacity-80'}`} />
      
      {/* Animated gradient overlay for depth - darker when video is loaded */}
      <div className={`absolute inset-0 bg-gradient-to-br from-purple-600/40 via-transparent to-blue-600/40 ${videoLoaded && !videoError ? 'opacity-30' : 'opacity-40'} animate-pulse`} />
      
      <style>{`
        .video-bg {
          animation: slowZoom 20s ease-in-out infinite alternate;
        }
        
        @keyframes slowZoom {
          0% {
            transform: scale(1.1);
          }
          100% {
            transform: scale(1.15);
          }
        }
      `}</style>
    </div>
  )
}

export default VideoBackground


import React, { Suspense, useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment } from '@react-three/drei';

// Avatar model component with enhanced lip sync
function AvatarModel({ isTyping, isSpeaking, baseX = 0, baseY = -4, baseZ = -2 }) {
  const { scene } = useGLTF('/brunette.glb');
  const modelRef = useRef();
  const headRef = useRef();
  const jawRef = useRef();
  const [morphTargets, setMorphTargets] = useState([]);
  
  // Animation state
  const animState = useRef({
    mouthOpen: 0,
    jawRotation: 0,
    headTilt: 0,
    blinkTimer: 0,
    speechIntensity: 0
  });

  // Find mesh parts on mount
  useEffect(() => {
    const foundMorphs = [];
    
    scene.traverse((child) => {
      if (child.isMesh) {
        // Try to find head/face mesh
        if (child.name.toLowerCase().includes('head') || 
            child.name.toLowerCase().includes('face')) {
          headRef.current = child;
        }
        
        // Try to find jaw mesh
        if (child.name.toLowerCase().includes('jaw') ||
            child.name.toLowerCase().includes('mouth')) {
          jawRef.current = child;
        }
        
        // Check for morph targets
        if (child.morphTargetInfluences && child.morphTargetDictionary) {
          foundMorphs.push({
            mesh: child,
            influences: child.morphTargetInfluences,
            dictionary: child.morphTargetDictionary
          });
          
          console.log('Found morph targets:', Object.keys(child.morphTargetDictionary));
        }
      }
    });
    
    setMorphTargets(foundMorphs);
    
    if (foundMorphs.length === 0) {
      console.warn('⚠️ No morph targets found - using rotation-based animation');
    }
  }, [scene]);

  useFrame((state) => {
    if (!modelRef.current) return;
    
    const time = state.clock.getElapsedTime();
    const deltaTime = state.clock.getDelta();
    
    // Base position with breathing
    modelRef.current.position.y = baseY + Math.sin(time * 1.5) * 0.02;
    modelRef.current.position.x = baseX;
    modelRef.current.position.z = baseZ;

    // Speaking Animation
    if (isSpeaking) {
      // Animate speech intensity (smooth ramp up/down)
      animState.current.speechIntensity = Math.min(
        animState.current.speechIntensity + deltaTime * 3,
        1
      );
      
      // Head movement while speaking
      modelRef.current.rotation.y = Math.sin(time * 3) * 0.08;
      modelRef.current.rotation.x = Math.sin(time * 2.5) * 0.03;
      modelRef.current.position.x = baseX + Math.sin(time * 4) * 0.015;
      
      // Mouth opening - varies speed and amplitude
      const speechWave = Math.abs(Math.sin(time * 8 + Math.sin(time * 3) * 0.5));
      animState.current.mouthOpen = speechWave * 0.5 * animState.current.speechIntensity;
      animState.current.jawRotation = speechWave * 0.15 * animState.current.speechIntensity;
      
    } else if (isTyping) {
      // Typing animation - thoughtful look
      animState.current.speechIntensity = Math.max(
        animState.current.speechIntensity - deltaTime * 2,
        0
      );
      
      modelRef.current.rotation.y = Math.sin(time * 1) * 0.1;
      modelRef.current.rotation.x = Math.sin(time * 0.8) * 0.04;
      
      // Gentle mouth movement
      animState.current.mouthOpen = Math.max(
        animState.current.mouthOpen - deltaTime * 2,
        0
      );
      animState.current.jawRotation = Math.max(
        animState.current.jawRotation - deltaTime * 2,
        0
      );
      
    } else {
      // Idle animation
      animState.current.speechIntensity = Math.max(
        animState.current.speechIntensity - deltaTime * 2,
        0
      );
      
      modelRef.current.rotation.y = Math.sin(time * 0.3) * 0.12;
      modelRef.current.rotation.x = Math.sin(time * 0.5) * 0.02;
      
      animState.current.mouthOpen = 0;
      animState.current.jawRotation = 0;
    }

    // Apply animations to mesh
    applyMouthAnimation(animState.current.mouthOpen, animState.current.jawRotation);
    
    // Random blinking
    animState.current.blinkTimer += deltaTime;
    if (animState.current.blinkTimer > 3 + Math.random() * 2) {
      applyBlink();
      animState.current.blinkTimer = 0;
    }
  });

  // Apply mouth animation using morph targets OR rotation
  const applyMouthAnimation = (openAmount, jawRotation) => {
    if (morphTargets.length > 0) {
      // Use morph targets if available
      morphTargets.forEach(({ mesh, influences, dictionary }) => {
        // Try common morph target names for mouth
        const mouthTargets = [
          'mouthOpen', 'mouth_open', 'viseme_aa', 'jawOpen', 'jaw_open',
          'A', 'aa', 'MouthOpen', 'Mouth_Open'
        ];
        
        mouthTargets.forEach(targetName => {
          if (dictionary[targetName] !== undefined) {
            const index = dictionary[targetName];
            influences[index] = openAmount * 2; // Scale up the effect
          }
        });
      });
    } else {
      // Fallback: Use jaw rotation if we found a jaw bone
      if (jawRef.current) {
        jawRef.current.rotation.x = jawRotation;
      }
      
      // Or rotate the entire head slightly
      if (headRef.current) {
        headRef.current.rotation.x = jawRotation * 0.3;
      }
    }
  };

  // Apply blinking animation
  const applyBlink = () => {
    if (morphTargets.length > 0) {
      morphTargets.forEach(({ mesh, influences, dictionary }) => {
        const blinkTargets = ['eyesClosed', 'eyes_closed', 'blink', 'Blink'];
        
        blinkTargets.forEach(targetName => {
          if (dictionary[targetName] !== undefined) {
            const index = dictionary[targetName];
            // Quick blink
            influences[index] = 1;
            setTimeout(() => {
              influences[index] = 0;
            }, 150);
          }
        });
      });
    }
  };

  return <primitive ref={modelRef} object={scene} scale={1.8} />;
}

// Main Avatar3D component
export default function Avatar3D({
  isTyping = false,
  isSpeaking = false,
  showControls = false,
  baseX = 0,
  baseY = -1.3,
  baseZ = -2,
  cameraPosition = [0, 0.2, 2],
  zoom = 30
}) {
  return (
    <div className="w-full h-full bg-gradient-to-br from-purple-50 to-indigo-50">
      <Canvas camera={{ position: cameraPosition, fov: 25 }} shadows>
        {/* Enhanced lighting for better visibility */}
        <ambientLight intensity={0.7} />
        <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
        <directionalLight position={[-5, 3, -2]} intensity={0.4} color="#b794f6" />
        <spotLight 
          position={[-5, 5, 2]} 
          intensity={0.4} 
          angle={0.3} 
          penumbra={1} 
          color="#8b5cf6" 
        />
        
        <Suspense fallback={null}>
          <AvatarModel 
            isTyping={isTyping} 
            isSpeaking={isSpeaking} 
            baseX={baseX} 
            baseY={baseY} 
            baseZ={baseZ} 
          />
          <Environment preset="city" />
        </Suspense>
        
        {showControls && (
          <OrbitControls
            enableZoom={true}
            minDistance={1}
            maxDistance={10}
          />
        )}
      </Canvas>
    </div>
  );
}

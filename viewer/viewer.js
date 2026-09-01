/**
 * Aurelia-chan — 3D Canon Viewer Engine
 * =====================================
 * Three.js viewer for inspecting AI-generated Aurelia models
 * against the canonical master sheets.
 *
 * Features:
 *   - GLB model loading (file input, drag-drop, default path)
 *   - Orbit controls with smooth damping
 *   - Studio lighting (3-point + environment)
 *   - Wireframe toggle
 *   - Auto-rotate
 *   - Screenshot export
 *   - Real-time model info display
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// ─── State ─────────────────────────────────────────────────────────────────

let renderer, scene, camera, controls, clock;
let currentModel = null;
let isWireframe = false;
let isAutoRotate = false;

// ─── DOM Elements ──────────────────────────────────────────────────────────

const canvas = document.getElementById('viewerCanvas');
const container = document.getElementById('canvasContainer');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingSubtext = document.getElementById('loadingSubtext');
const dropOverlay = document.getElementById('dropOverlay');
const modelInfo = document.getElementById('modelInfo');
const measurementBadge = document.getElementById('measurementBadge');
const measureHeight = document.getElementById('measureHeight');

// Buttons
const btnWireframe = document.getElementById('btnWireframe');
const btnReset = document.getElementById('btnReset');
const btnScreenshot = document.getElementById('btnScreenshot');
const btnAutoRotate = document.getElementById('btnAutoRotate');
const btnLoadDefault = document.getElementById('btnLoadDefault');
const fileInput = document.getElementById('fileInput');
const btnApprove = document.getElementById('btnApprove');
const btnReject = document.getElementById('btnReject');

// Lighting controls
const lightIntensity = document.getElementById('lightIntensity');
const envSelect = document.getElementById('envSelect');

// ─── Initialization ────────────────────────────────────────────────────────

function init() {
    clock = new THREE.Clock();

    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true,
        alpha: false,
        preserveDrawingBuffer: true, // For screenshots
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0E0E12);

    // Environment map for PBR materials
    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    const envTexture = pmremGenerator.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = envTexture;
    pmremGenerator.dispose();

    // Camera
    camera = new THREE.PerspectiveCamera(
        35,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1.0, 3.5);

    // Controls
    controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.set(0, 0.85, 0);
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.maxPolarAngle = Math.PI * 0.85;
    controls.update();

    // Lighting — 3-point studio setup
    setupLighting();

    // Ground plane (subtle)
    const groundGeo = new THREE.CircleGeometry(3, 64);
    const groundMat = new THREE.MeshStandardMaterial({
        color: 0x141418,
        roughness: 0.9,
        metallic: 0.0,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid helper (very subtle)
    const grid = new THREE.GridHelper(6, 30, 0x1A1A22, 0x1A1A22);
    grid.position.y = 0.001;
    grid.material.opacity = 0.3;
    grid.material.transparent = true;
    scene.add(grid);

    // Events
    window.addEventListener('resize', onResize);
    setupDragDrop();
    setupButtonEvents();

    // Start render loop
    animate();

    // Hide loading (no model loaded yet)
    loadingOverlay.classList.add('hidden');
}

function setupLighting() {
    // Remove existing lights
    scene.children
        .filter(c => c.isLight)
        .forEach(l => scene.remove(l));

    // Ambient fill
    const ambient = new THREE.AmbientLight(0xffffff, 0.3);
    scene.add(ambient);

    // Key light (warm, from upper right)
    const keyLight = new THREE.DirectionalLight(0xFFF5E6, 1.2);
    keyLight.position.set(3, 5, 3);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(2048, 2048);
    keyLight.shadow.camera.near = 0.1;
    keyLight.shadow.camera.far = 20;
    keyLight.shadow.camera.left = -3;
    keyLight.shadow.camera.right = 3;
    keyLight.shadow.camera.top = 3;
    keyLight.shadow.camera.bottom = -3;
    keyLight.shadow.bias = -0.001;
    keyLight.name = 'keyLight';
    scene.add(keyLight);

    // Fill light (cool, from left)
    const fillLight = new THREE.DirectionalLight(0xE6F0FF, 0.5);
    fillLight.position.set(-4, 3, 1);
    fillLight.name = 'fillLight';
    scene.add(fillLight);

    // Rim light (warm gold accent from behind)
    const rimLight = new THREE.DirectionalLight(0xC9A227, 0.4);
    rimLight.position.set(0, 3, -4);
    rimLight.name = 'rimLight';
    scene.add(rimLight);

    // Bottom fill (very subtle, prevents harsh under-shadows)
    const bottomFill = new THREE.DirectionalLight(0xF6EDE6, 0.15);
    bottomFill.position.set(0, -2, 2);
    scene.add(bottomFill);
}

// ─── Model Loading ─────────────────────────────────────────────────────────

const gltfLoader = new GLTFLoader();

// Set up Draco decoder
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://unpkg.com/three@0.170.0/examples/jsm/libs/draco/');
gltfLoader.setDRACOLoader(dracoLoader);

function loadModel(source) {
    // Show loading
    loadingOverlay.classList.remove('hidden');
    loadingSubtext.textContent = 'Loading model...';

    // Remove previous model
    if (currentModel) {
        scene.remove(currentModel);
        currentModel.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(m => m.dispose());
                } else {
                    child.material.dispose();
                }
            }
        });
        currentModel = null;
    }

    const onLoad = (gltf) => {
        currentModel = gltf.scene;

        // Center and scale model
        const box = new THREE.Box3().setFromObject(currentModel);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());

        // Move model so feet are at y=0
        currentModel.position.y = -box.min.y;
        // Center horizontally
        currentModel.position.x = -center.x;
        currentModel.position.z = -center.z;

        // Enable shadows
        currentModel.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });

        scene.add(currentModel);

        // Update camera to frame the model
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(0, size.y * 0.5, maxDim * 2.5);
        controls.target.set(0, size.y * 0.45, 0);
        controls.update();

        // Update info
        updateModelInfo(gltf, size);

        // Update measurement badge
        // Assuming the model height represents the character height
        // The actual cm depends on the model's scale
        const heightCm = (size.y * 100).toFixed(1); // If 1 unit = 1m
        measureHeight.textContent = heightCm;

        // Hide loading
        loadingOverlay.classList.add('hidden');

        console.log('Model loaded successfully:', size);
    };

    const onProgress = (event) => {
        if (event.lengthComputable) {
            const pct = Math.round((event.loaded / event.total) * 100);
            loadingSubtext.textContent = `Loading... ${pct}%`;
        }
    };

    const onError = (error) => {
        console.error('Failed to load model:', error);
        loadingSubtext.textContent = `Error: ${error.message || 'Failed to load model'}`;
        setTimeout(() => loadingOverlay.classList.add('hidden'), 3000);
    };

    if (typeof source === 'string') {
        // URL or path
        gltfLoader.load(source, onLoad, onProgress, onError);
    } else if (source instanceof ArrayBuffer) {
        // Dropped/selected file
        gltfLoader.parse(source, '', onLoad, onError);
    }
}

function updateModelInfo(gltf, size) {
    let meshCount = 0;
    let totalVerts = 0;
    let totalFaces = 0;
    let materialSet = new Set();

    gltf.scene.traverse((child) => {
        if (child.isMesh) {
            meshCount++;
            totalVerts += child.geometry.attributes.position?.count || 0;
            const index = child.geometry.index;
            totalFaces += index ? index.count / 3 : (child.geometry.attributes.position?.count || 0) / 3;

            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(m => materialSet.add(m.name || 'unnamed'));
                } else {
                    materialSet.add(child.material.name || 'unnamed');
                }
            }
        }
    });

    const hasAnimations = gltf.animations && gltf.animations.length > 0;
    const animCount = gltf.animations ? gltf.animations.length : 0;

    modelInfo.innerHTML = `
        <span class="info-label">${Math.round(totalFaces).toLocaleString()} faces</span>
        <span class="info-label">${materialSet.size} materials</span>
        <span class="info-label">${meshCount} meshes</span>
        ${hasAnimations ? `<span class="info-label">${animCount} anims</span>` : ''}
    `;

    // Show validation section
    const valSection = document.getElementById('validationSection');
    const valGrid = document.getElementById('validationGrid');
    valSection.style.display = 'block';

    valGrid.innerHTML = `
        <div class="val-item ${totalFaces <= 80000 ? 'pass' : 'fail'}">
            <span class="val-label">Polygons</span>
            <span class="val-value">${Math.round(totalFaces).toLocaleString()} / 80K</span>
        </div>
        <div class="val-item ${materialSet.size <= 15 ? 'pass' : 'fail'}">
            <span class="val-label">Materials</span>
            <span class="val-value">${materialSet.size} / 15</span>
        </div>
        <div class="val-item info">
            <span class="val-label">Meshes</span>
            <span class="val-value">${meshCount}</span>
        </div>
        <div class="val-item info">
            <span class="val-label">Height</span>
            <span class="val-value">${(size.y * 100).toFixed(1)} cm</span>
        </div>
        <div class="val-item ${hasAnimations ? 'pass' : 'info'}">
            <span class="val-label">Animations</span>
            <span class="val-value">${animCount > 0 ? animCount : 'None'}</span>
        </div>
    `;
}

// ─── Event Handlers ────────────────────────────────────────────────────────

function setupButtonEvents() {
    // Load default model
    btnLoadDefault.addEventListener('click', () => {
        const defaultPath = '../assets/web/aurelia.glb';
        
        // Check if default model exists by attempting to fetch it
        fetch(defaultPath)
            .then(response => {
                if (response.ok) {
                    loadModel(defaultPath);
                } else {
                    alert('Default model not found. Please generate a 3D model first using the pipeline, or load a GLB file manually.');
                }
            })
            .catch(() => {
                alert('Unable to access default model. Please load a GLB file manually using the "Browse GLB..." button.');
            });
    });

    // File input
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => loadModel(ev.target.result);
            reader.readAsArrayBuffer(file);
        }
    });

    // Wireframe toggle
    btnWireframe.addEventListener('click', () => {
        isWireframe = !isWireframe;
        btnWireframe.classList.toggle('active', isWireframe);

        if (currentModel) {
            currentModel.traverse((child) => {
                if (child.isMesh && child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.wireframe = isWireframe);
                    } else {
                        child.material.wireframe = isWireframe;
                    }
                }
            });
        }
    });

    // Reset camera
    btnReset.addEventListener('click', () => {
        if (currentModel) {
            const box = new THREE.Box3().setFromObject(currentModel);
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);

            camera.position.set(0, size.y * 0.5, maxDim * 2.5);
            controls.target.set(0, size.y * 0.45, 0);
            controls.update();
        } else {
            camera.position.set(0, 1.0, 3.5);
            controls.target.set(0, 0.85, 0);
            controls.update();
        }
    });

    // Screenshot
    btnScreenshot.addEventListener('click', () => {
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = `aurelia_3d_${Date.now()}.png`;
        link.href = dataURL;
        link.click();
    });

    // Auto-rotate
    btnAutoRotate.addEventListener('click', () => {
        isAutoRotate = !isAutoRotate;
        controls.autoRotate = isAutoRotate;
        controls.autoRotateSpeed = 2.0;
        btnAutoRotate.classList.toggle('active', isAutoRotate);
    });

    // Environment select
    envSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        switch (val) {
            case 'studio':
                scene.background = new THREE.Color(0x0E0E12);
                renderer.toneMappingExposure = 1.0;
                break;
            case 'outdoor':
                scene.background = new THREE.Color(0x1A2030);
                renderer.toneMappingExposure = 1.2;
                break;
            case 'warm':
                scene.background = new THREE.Color(0x1A1610);
                renderer.toneMappingExposure = 0.9;
                break;
            case 'neutral':
                scene.background = new THREE.Color(0x2A2A2A);
                renderer.toneMappingExposure = 1.0;
                break;
        }
    });

    // Light intensity
    lightIntensity.addEventListener('input', (e) => {
        const intensity = parseFloat(e.target.value);
        scene.children.forEach(child => {
            if (child.isDirectionalLight) {
                if (child.name === 'keyLight') child.intensity = 1.2 * intensity;
                else if (child.name === 'fillLight') child.intensity = 0.5 * intensity;
                else if (child.name === 'rimLight') child.intensity = 0.4 * intensity;
                else child.intensity = 0.15 * intensity;
            }
        });
    });

    // Environment select
    envSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        switch (val) {
            case 'studio':
                scene.background = new THREE.Color(0x0E0E12);
                renderer.toneMappingExposure = 1.0;
                break;
            case 'outdoor':
                scene.background = new THREE.Color(0x1A2030);
                renderer.toneMappingExposure = 1.2;
                break;
            case 'warm':
                scene.background = new THREE.Color(0x1A1610);
                renderer.toneMappingExposure = 0.9;
                break;
            case 'neutral':
                scene.background = new THREE.Color(0x2A2A2A);
                renderer.toneMappingExposure = 1.0;
                break;
        }
    });

    // Approve / Reject
    btnApprove.addEventListener('click', () => {
        const checkedCount = document.querySelectorAll('.qa-item input:checked').length;
        const totalItems = document.querySelectorAll('.qa-item input').length;

        if (checkedCount < totalItems) {
            alert(`Please review all ${totalItems} items before approving.\n${checkedCount}/${totalItems} checked.`);
            return;
        }

        alert('✓ Model APPROVED for production pipeline.\n\nNext steps:\n1. Run material setup (blender/materials.py)\n2. Run optimization (blender/optimize.py)\n3. Export web GLB (blender/export.py)');
    });

    // Initialize checkbox state handling for CSS compatibility
    document.querySelectorAll('.qa-item input').forEach(checkbox => {
        const qaItem = checkbox.closest('.qa-item');
        if (checkbox.checked) {
            qaItem.classList.add('checked');
        }
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                qaItem.classList.add('checked');
            } else {
                qaItem.classList.remove('checked');
            }
        });
    });

    btnReject.addEventListener('click', () => {
        const unchecked = [];
        document.querySelectorAll('.qa-item').forEach(item => {
            if (!item.querySelector('input').checked) {
                unchecked.push(item.querySelector('span').textContent);
            }
        });

        const issues = unchecked.length > 0
            ? `\n\nFailed items:\n${unchecked.map(i => `  • ${i}`).join('\n')}`
            : '';

        alert(`✗ Model REJECTED.${issues}\n\nAction: Re-generate or apply Blender corrections.`);
    });
}

// ─── Drag & Drop ───────────────────────────────────────────────────────────

function setupDragDrop() {
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropOverlay.classList.add('active');
    });

    container.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropOverlay.classList.remove('active');
    });

    container.addEventListener('drop', (e) => {
        e.preventDefault();
        dropOverlay.classList.remove('active');

        const file = e.dataTransfer.files[0];
        if (file && (file.name.endsWith('.glb') || file.name.endsWith('.gltf'))) {
            const reader = new FileReader();
            reader.onload = (ev) => loadModel(ev.target.result);
            reader.readAsArrayBuffer(file);
        }
    });
}

// ─── Resize ────────────────────────────────────────────────────────────────

function onResize() {
    const width = container.clientWidth;
    const height = container.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
}

// ─── Animation Loop ────────────────────────────────────────────────────────

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// ─── Start ─────────────────────────────────────────────────────────────────

init();

var self = null;

var Beach = function() {
	self = this;
	
	self.debug = {
		stats: true
	};
	
	self.players = {
		local: null
	};
	
	self.terrain = {
		size: {
			x: 1200,
			y: 1200
		},
		resolution: {
			x: 10,
			y: 10
		},
		geometry: null
	};

	self.movement = {
		flags: {
			left: false,
			right: false
		},
		keys: {
			left: 65,
			right: 68,

			one: 49,
			two: 50,
			three: 51,
			four: 52,
			five: 53,
			six: 54,
			seven: 55,
			eight: 56,
			nine: 57,
			zero: 58
		},
		speed: 15
	};
	
	self.container = self.createContainer();
	self.scene = self.createScene();
	self.sceneMain();
	self.camera = self.createCamera();
	self.renderer = self.createRenderer();
	
	self.terrain.geometry = self.createTerrain();
	
	self.setupEvents();
};

Beach.prototype.toggleWater = function() {
	if (self.scene.getChildByName("Water") == null) {
		self.scene.add(self.water);
	} else {
		self.scene.remove(self.water);
	}
};

Beach.prototype.createTerrain = function() {
	var geometry = new THREE.PlaneGeometry(
		self.terrain.size.x,
		self.terrain.size.y,
		self.terrain.resolution.x,
		self.terrain.resolution.y
	);
	geometry.dynamic = true;
	self.buildTerrain(geometry);
	return geometry;
};

Beach.prototype.buildTerrain = function(geometry) {
	// var texture = self.createTerrainTexture();
	var mesh = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({color: 0xcccccc}));
	mesh.rotation.x = -90 * Math.PI / 180;
	self.scene.remove(self.scene.getChildByName("Terrain"));
	mesh.name = "Terrain";
	self.scene.add(mesh);
};

Beach.prototype.applyTerrainTransform = function(fn) {
	var geometry = fn(self.terrain.geometry);
	geometry.__dirtyVertices = true;
	geometry.computeCentroids();
	self.buildTerrain(geometry);
	self.terrain.geometry = geometry;
	return geometry;
};

Beach.prototype.terrainRandomHeightMap = function(geometry) {
	var noise = new SimplexNoise();
	var n;
	
	var factorX = 5;
	var factorY = 3;
	var factorZ = 15;
	
	for (var i = 0; i < geometry.vertices.length; i++) {
		n = noise.noise(geometry.vertices[i].x / self.terrain.resolution.x / factorX, geometry.vertices[i].y / self.terrain.resolution.y / factorY);
		n -= 0.5;
		geometry.vertices[i].z = n * factorZ;
	}
	return geometry;
};

Beach.prototype.raiseTerrain = function(geometry) {
	for (var i = 0; i < geometry.vertices.length; i++) {
		geometry.vertices[i].z += 3;
	}
	return geometry;
};

Beach.prototype.lowerTerrain = function(geometry) {
	for (var i = 0; i < geometry.vertices.length; i++) {
		geometry.vertices[i].z -= 3;
	}
	return geometry;
};

Beach.prototype.rollingParticle = function(geometry) {
	var peaks = Math.floor(Math.random() * 4) + 1;
	console.log(peaks);
	var maxDistance = 200;
	var peakPosition, refPeak, distance;
	for (var p = 0; p < peaks; p++) {
		peakPosition = new THREE.Vector3(Math.random() * self.terrain.size.x / 3 * 2, Math.random() * self.terrain.size.y / 3 * 2, 0);
		peakPosition = peakPosition.subSelf(new THREE.Vector3(self.terrain.size.x / 3, self.terrain.size.y / 3, 0));

		for (var i = 0; i < geometry.vertices.length; i++) {
			refPeak = peakPosition.clone();
			refPeak.z = geometry.vertices[i].z;
			distance = geometry.vertices[i].position.distanceTo(refPeak);
			if (distance <= maxDistance) {
				geometry.vertices[i].z += (maxDistance - distance) / 20;
			} else {
				geometry.vertices[i].z += (maxDistance - distance) / 200;
			}
		}
	}
	return geometry;
};

Beach.prototype.smoothFlatten = function(geometry) {
	var factor = document.getElementById('SmoothFactor').value;
	for (var i = 0; i < geometry.vertices.length; i++) {
		// geometry.vertices[i].z += (3) * factor;
	}
	return geometry;
};

Beach.prototype.createTerrainTexture = function() {
	return new THREE.Texture(
		generateTexture(data, worldWidth, worldDepth),
		new THREE.UVMapping(),
		THREE.ClampToEdgeWrapping,
		THREE.ClampToEdgeWrapping
	);
};

Beach.prototype.createContainer = function() {
	var div = document.createElement('div');
	document.body.appendChild(div);
	return div;
};

Beach.prototype.createScene = function() {
	return new THREE.Scene();
};

Beach.prototype.createSky = function(){
	var M = 1000 * 10;
	var skyGeometry = new THREE.CubeGeometry(M, M, M, 4, 4, 4, null, true);
	var skyMaterial = new THREE.MeshBasicMaterial({color: 0x3030ff});
	var skyboxMesh  = new THREE.Mesh(skyGeometry, skyMaterial);
	skyboxMesh.flipSided = true;
	self.scene.add(skyboxMesh);
};

Beach.prototype.sceneMain = function() {
	var pointLight = new THREE.PointLight(0xffffcc);
	pointLight.intensity = 1;
	pointLight.position = new THREE.Vector3(1000, 800, -1000);
	self.scene.add(pointLight);
	self.createSky();
	var waterGeom = new THREE.PlaneGeometry(self.terrain.size.x, self.terrain.size.y, 1, 1);
	var waterMesh = new THREE.Mesh(waterGeom, new THREE.MeshLambertMaterial({color: 0x6699ff}));
	waterMesh.rotation.x = -90 * Math.PI / 180;
	waterMesh.name = "Water";
	self.water = waterMesh;
	
	var refObj, refMat, refMesh, refGeom;

	refObj = new THREE.CubeGeometry(1500, 50, 1200);
	refMat = new THREE.MeshBasicMaterial({color: 0xcccccc});
	refMesh = new THREE.Mesh(refObj, refMat);
	refMesh.position = new THREE.Vector3(0, 0, 0);
	//self.scene.add(refMesh);
};

Beach.prototype.createCamera = function() {
	var camera = new THREE.PerspectiveCamera(
		65,                                     // Field of View
		window.innerWidth / window.innerHeight, // Aspect Ratio
		10,                                     // Near clipping plane
		5000                                    // Far clipping plane
	);
	camera.position = new THREE.Vector3(0, 600, 1000);
	camera.lookAt(new THREE.Vector3(0, 0, 0));
	self.scene.add(camera);
	return camera;
};

Beach.prototype.createRenderer = function() {
	var renderer;
	try {
		renderer = new THREE.WebGLRenderer();
	} catch(e) {
		renderer = new THREE.CanvasRenderer();
	}
	renderer.setSize(window.innerWidth, window.innerHeight);
	self.container.appendChild(renderer.domElement);
	return renderer;
};

Beach.prototype.render = function() {
	self.renderer.render(self.scene, self.camera);
};

Beach.prototype.setupEvents = function() {
	// document.addEventListener('mousemove', self.mouseMoved, false);
	document.addEventListener('keydown', self.keyDown, false);
	document.addEventListener('keyup', self.keyUp, false);
};

Beach.prototype.keyEvent = function(keycode, state) {
	var keys = self.movement.keys;
	switch (keycode) {
		case keys.left:
			self.movement.flags.left = state;
			break;
		case keys.right:
			self.movement.flags.right = state;
			break;
		case keys.one:
			state && self.applyTerrainTransform(self.terrainRandomHeightMap);
			break;
		case keys.two:
			state && self.toggleWater();
			break;
		case keys.three:
			state && self.applyTerrainTransform(self.raiseTerrain);
			break;
		case keys.four:
			state && self.applyTerrainTransform(self.lowerTerrain);
			break;
		case keys.five:
			state && self.applyTerrainTransform(self.rollingParticle);
			break;
	}
};

Beach.prototype.keyUp = function(event) {
	self.keyEvent(event.keyCode, false);
};

Beach.prototype.keyDown = function(event) {
	self.keyEvent(event.keyCode, true);
};

Beach.prototype.motion = function() {
	var zero = new THREE.Vector3(0, 0, 0);
	var direction = zero;
	var move = false;
	if (self.movement.flags.left) {
		self.camera.x -= self.movement.speed;
		move = true;
	}
	if (self.movement.flags.right) {
		self.camera.x += self.movement.speed;
		move = true;
	}

	if (move) {
		// direction.setLength(self.movement.speed);
		self.camera.lookAt(new THREE.Vector3(0, 0, 0));
	}
};


Beach.prototype.run = function(fps) {
	self.motion();
	self.render();
	setTimeout(
		function() {
			self.run(fps);
		},
		1 / fps * 1000
	);
}

var myClient = new Beach({
});
myClient.run(60);

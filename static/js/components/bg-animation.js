// Inspired by https://codepen.io/Souzou/pen/KKzQMwB :)

class App {
  constructor() {
    this.dom = document.querySelector("#bg-wrapper");
    this.canvas = this.dom.querySelector("#my-canvas");
    this.vertex = document.querySelector("#vertex").textContent;
    this.fragment = document.querySelector("#fragment").textContent;
    this.width = this.dom.offsetWidth;
    this.height = this.dom.offsetHeight;

    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
    this.renderer.setSize(this.width, this.height);

    this.camera = new THREE.PerspectiveCamera(70, this.width / this.height, 0.001, 1000);
    this.camera.position.set(0, 0, 1);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xffffff);

    this.guiSettings = {
      distortion: "0", // Changer ici !
    };
    this.gui = new dat.GUI();
    this.gui.domElement.style.display = "none";
    this.gui.add(this.guiSettings, "distortion", {
      "Static": "0",
      "Blow In": "1",
      "Blow Out": "2",
      "Wave Left": "3",
      "Wave Right": "4",
      "Wave Down": "5",
      "Wave Up": "6",
      "Blow In + Wave Left": "7",
      "Blow In + Wave Right": "8",
      "Blow In + Wave Down": "9",
      "Blow In + Wave Up": "10",
      "Diagonal Wave": "11",
    });

    this.addObjects();
    this.render();
    this.initEvents();
    this.onResize();
  }

  addObjects() {
    this.textureLoader = new THREE.TextureLoader();
    this.planeMat = new THREE.ShaderMaterial({
      side: THREE.DoubleSide,
      // Réglages des sinus
      uniforms: {
        u_time: { type: "f", value: 0.2 },
        u_resolution: { type: "v4", value: new THREE.Vector4() },
        u_strength: { type: "f", value: 10.0 },
        u_speed: { type: "f", value: 0.6 },
        u_texture: { type: "t", value: this.textureLoader.load("./static/assets/black-paper.png") },
        u_distortion: { type: "i", value: parseInt(this.guiSettings.distortion) },
      },
      vertexShader: this.vertex,
      fragmentShader: this.fragment,
      transparent: true,
    });

    this.planeGeo = new THREE.PlaneBufferGeometry(1, 1, 100, 100);
    this.plane = new THREE.Mesh(this.planeGeo, this.planeMat);
    this.scene.add(this.plane);
  }

  render() {
    this.planeMat.uniforms.u_time.value += 0.01;
    this.planeMat.uniforms.u_distortion.value = parseInt(this.guiSettings.distortion);

    requestAnimationFrame(this.render.bind(this));
    this.renderer.render(this.scene, this.camera);
  }

  initEvents() {
    window.addEventListener("resize", this.onResize.bind(this));
  }

  onResize() {
    this.width = this.dom.offsetWidth;
    this.height = this.dom.offsetHeight;
    this.renderer.setSize(this.width, this.height);
    this.camera.aspect = this.width / this.height;

    let a1, a2;
    const imageAspect = 2560 / 1707;
    if (this.height / this.width < imageAspect) {
      a2 = ((1 / imageAspect) * this.height) / this.width;
      a1 = 1;
    } else {
      a2 = 1;
      a1 = (this.width / this.height) * imageAspect;
    }
    this.planeMat.uniforms.u_resolution.value.set(this.width, this.height, a1, a2);
    this.camera.zoom = 3;
    this.camera.updateProjectionMatrix();
  }
}

new App();

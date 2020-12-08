export default (Hlsjs, upimgConfig) => {
  const loader = class Loader extends Hlsjs.DefaultConfig.loader {
    constructor(config) {
      super(config)
      const load = this.load.bind(this)
      this.load = function (context, config, callbacks) {
        if (context.type === 'manifest') {
			context.responseType="arraybuffer"
          const onSuccess = callbacks.onSuccess
          callbacks.onSuccess = function (response, stats, context) {
            let data = response.data
				    data = String.fromCharCode.apply(null, new Uint8Array(data));
            response.data = data
            onSuccess(response, stats, context)
          }
        }
        if (context.responseType === 'arraybuffer') {
          const onSuccess = callbacks.onSuccess
          callbacks.onSuccess = function (response, stats, context) {
            let promise = IJS.Image.load(response.data)
            promise.then((image)=>{
              let mask = new ImageMask({debug: false});
              let colorMask = new ImageColorMask(image.data, mask);
              let fileLength = colorMask.readNumberBySize(mask.opts.lengthSize);
              console.log("fileLength:"+fileLength)
              let buffer = new ArrayBuffer(fileLength);
              let imageData = new Uint8Array(buffer);
              for (var i = 0; i < fileLength; i++) {
                var b = colorMask.readNumberBySize(8);
                imageData[i] = b;
              }
              response.data = imageData
              onSuccess(response, stats, context)
            }, (error)=>{
              console.log(error)
            })
			
          }
        }
        load(context, config, callbacks)
      }
    }
  }
  return loader
}

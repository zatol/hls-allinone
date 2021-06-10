/**
 * Allows to generate an array of points for a binary image (bit depth = 1)
 * The points consider the beginning and the end of each pixel
 * @memberof Image
 * @instance
 * @return {Array<Array<number>>} - an array of [x,y] corresponding to the set pixels in the binary image
 */
export default function extendedPoints() {
  this.checkProcessable('extendedPoints', {
    bitDepth: [1],
  });

  const pixels = [];
  for (let y = 0; y < this.height; y++) {
    for (let x = 0; x < this.width; x++) {
      if (this.getBitXY(x, y) === 1) {
        pixels.push([x, y]);
        if (this.getBitXY(x + 1, y) !== 1) {
          pixels.push([x + 1, y]);
          pixels.push([x + 1, y + 1]);
          if (this.getBitXY(x, y + 1) !== 1) {
            pixels.push([x, y + 1]);
          }
        } else {
          if (this.getBitXY(x, y + 1) !== 1) {
            pixels.push([x, y + 1]);
            pixels.push([x + 1, y + 1]);
          }
        }
      }
    }
  }
  return pixels;
}

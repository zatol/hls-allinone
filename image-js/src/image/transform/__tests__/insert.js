import binary from 'test/binary';
import { Image } from 'test/common';

test('insert on grey image', function () {
  let img = new Image(
    3,
    4,
    [100, 200, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200],
    { kind: 'GREY' },
  );

  let toInsert = new Image(2, 2, [0, 255, 0, 0], { kind: 'GREY' });

  expect(img.insert(toInsert).data).toStrictEqual([
    0,
    255,
    100,
    0,
    0,
    100,
    100,
    100,
    100,
    100,
    100,
    200,
  ]);
});

test('insert on binary image', function () {
  let mask = binary`
    11111
    11111
    11111
    11111
    11111
  `;

  let toInsert = binary`
    0001
    0101
    0001
  `;

  expect(mask.insert(toInsert).data).toStrictEqual(
    binary`
        00011
        01011
        00011
        11111
        11111
    `.data,
  );

  expect(
    mask.insert(toInsert, {
      x: 1,
      y: 1,
    }).data,
  ).toStrictEqual(
    binary`
      11111
      10001
      10101
      10001
      11111
    `.data,
  );

  expect(
    mask.insert(toInsert, {
      x: 4,
      y: 4,
    }).data,
  ).toStrictEqual(
    binary`
      11111
      11111
      11111
      11111
      11110
    `.data,
  );
});

/*
 * Saving a landscape as a picture (PRD §1.5, §5.4).
 *
 * Constraint 13b: exports default to the contour twin. A rendered hill is a
 * picture of a landscape; a contour is a landscape you can measure off the
 * page. So the snapshot draws the top-down view, in black on white, at a size
 * that prints — and it does it from the same density grid the surface is drawn
 * from, so what saves is what was on screen.
 *
 * §5b asks for alt text on exported images stating the chart type and the key
 * finding. A PNG file carries no alt attribute, so the finding goes into the
 * filename, which is what a person actually sees when they come back to it.
 */

import { contourSegments, TRIANGLE_HEIGHT } from "./terrain.js";

const SIZE = 900;
const PAD = 90;

/** A filename that says what the picture shows (§5b alt-text rule). */
export function snapshotFilename(landscape, framework) {
  const panel = landscape?.panels?.[0];
  const slug = (text) =>
    String(text ?? "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  const finding = panel?.peaks?.length
    ? `stories-cluster-near-${slug(panel.peaks[0].nearest_corner)}`
    : "no-clear-cluster";
  return `${slug(framework?.name) || "narrative-lens"}-v${framework?.version ?? 1}-${slug(
    panel?.title,
  )}-contour-${finding}.png`;
}

/**
 * Draw the contour twin to a canvas and hand it to the browser to save.
 *
 * Black on white, no colour at all: a snapshot is for printing and pasting into
 * a document, and §5b's print grammar says a photocopier is the test.
 */
export function saveContourSnapshot(panel, filename) {
  const canvas = document.createElement("canvas");
  const ratio = 2;
  canvas.width = SIZE * ratio;
  canvas.height = SIZE * ratio;
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);

  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, SIZE, SIZE);

  const plot = SIZE - PAD * 2;
  const toScreen = (x, y) => ({
    x: PAD + x * plot,
    y: PAD + (1 - y / TRIANGLE_HEIGHT) * plot,
  });

  const corners = [
    [0, 0],
    [1, 0],
    [0.5, TRIANGLE_HEIGHT],
  ].map(([x, y]) => toScreen(x, y));

  context.strokeStyle = "#000000";
  context.lineWidth = 1.5;
  context.beginPath();
  corners.forEach((point, index) =>
    index === 0 ? context.moveTo(point.x, point.y) : context.lineTo(point.x, point.y),
  );
  context.closePath();
  context.stroke();

  (panel.contour_levels ?? []).forEach((level, band) => {
    context.lineWidth = 1 + band * 0.7;
    context.beginPath();
    for (const [from, to] of contourSegments(
      panel.density,
      panel.x_axis,
      panel.y_axis,
      level,
    )) {
      const a = toScreen(from.x, from.y);
      const b = toScreen(to.x, to.y);
      context.moveTo(a.x, a.y);
      context.lineTo(b.x, b.y);
    }
    context.stroke();
  });

  context.fillStyle = "#000000";
  for (const point of panel.points ?? []) {
    const at = toScreen(point.x, point.y);
    context.beginPath();
    context.arc(at.x, at.y, 3.5, 0, Math.PI * 2);
    context.fill();
  }

  context.font = "20px ui-sans-serif, system-ui, sans-serif";
  for (const peak of panel.peaks ?? []) {
    const at = toScreen(peak.x, peak.y);
    context.beginPath();
    context.arc(at.x, at.y, 9, 0, Math.PI * 2);
    context.lineWidth = 2;
    context.stroke();
    context.textAlign = "center";
    context.fillText(String(peak.count), at.x, at.y - 16);
  }

  context.font = "18px ui-sans-serif, system-ui, sans-serif";
  const labels = [
    { text: panel.corners[0], at: corners[0], align: "right", dy: 26 },
    { text: panel.corners[1], at: corners[1], align: "left", dy: 26 },
    { text: panel.corners[2], at: corners[2], align: "center", dy: -18 },
  ];
  for (const label of labels) {
    context.textAlign = label.align;
    context.fillText(label.text, label.at.x, label.at.y + label.dy);
  }

  context.textAlign = "left";
  context.font = "22px ui-sans-serif, system-ui, sans-serif";
  context.fillText(panel.title, PAD, 44);
  context.font = "16px ui-sans-serif, system-ui, sans-serif";
  context.fillText(
    `${panel.count} ${panel.count === 1 ? "story" : "stories"} — contour of the narrative landscape`,
    PAD,
    68,
  );

  const link = document.createElement("a");
  link.download = filename;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

const cloud = document.getElementById('tagCloud');
if (!cloud) return 'no cloud';
const rect = cloud.getBoundingClientRect();
cloud.dispatchEvent(new MouseEvent('mousemove', {
  clientX: rect.left + rect.width / 2 + 200,
  clientY: rect.top + rect.height / 2 - 100,
  bubbles: true
}));
return 'done';

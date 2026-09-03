const style = document.createElement('style');
style.textContent = '@keyframes tagCloudDemo { 0% { transform: rotateX(-18deg) rotateY(22deg); } 50% { transform: rotateX(-12deg) rotateY(-18deg); } 100% { transform: rotateX(-18deg) rotateY(22deg); } } #tagCloud { animation: tagCloudDemo 5s ease-in-out infinite !important; }';
document.head.appendChild(style);
'done';

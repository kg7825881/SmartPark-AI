import '../styles/globals.css';
import 'leaflet/dist/leaflet.css';

export const metadata = {
  title: 'SmartPark AI Dashboard',
  description: 'Parking Congestion Decision Intelligence Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#0a0c10] text-[#f3f4f6]">
        {children}
      </body>
    </html>
  );
}
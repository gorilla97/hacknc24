import ChatWindow from "@/components/ChatWindow";
import Image from "next/image";


export default function Home() {
  return (
    <div className="items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <div className="justify-center align-middle">
        <h1 className="text-center scale-150 pb-4">Financial Assistant</h1>
      </div>
        <ChatWindow />
    </div>
  );
}

"use client"

import React from 'react'
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import LeftPanelNavigation from "@/components/LeftPanelNavigation";
import NavigationContent from "@/interfaces/NavigationContent";
// import Image from "next/image";


const navContents: NavigationContent[] = [
  {
    name: "Home",
    link: "#home"
  },
  {
    name: "About",
    link: "#about"
  },
  {
    name: "Projects",
    link: "#projects"
  },
  {
    name: "Contact",
    link: "#contact"
  }
]


const Home = () => {

  const [isOpenMenu, setIsOpenMenu] = React.useState(false);
  const [item, setItem] = React.useState("");

  React.useEffect(() => {
    setItem(navContents.find(nav => location.hash.includes(nav.link ?? ''))?.link ?? navContents[0]?.link ?? '');
  }, []);

  return (
    <>
      <div className='absolute w-full z-20'>
        <Header navContents={navContents} currentPath={item} onChange={setIsOpenMenu} isOpenMenu={isOpenMenu} />
      </div>
      <LeftPanelNavigation navContents={navContents} currentPath={item} onChange={setIsOpenMenu} isOpenMenu={isOpenMenu} />
      <div className='relative w-screen h-screen overflow-hidden transition duration-300'>
        <div className='w-full h-full overflow-auto'>
          <div className='invisible'>
            <Header />
          </div>
          <>
            {/** Main contents here */}
          </>
          <Footer />
        </div>
      </div>
    </>
  )
}

export default Home
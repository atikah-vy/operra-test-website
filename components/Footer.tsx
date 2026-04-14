import Image from 'next/image'
import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.footerLogo}>
          <Image
            src="/brand_logo_page/Brand LOGO.jpg"
            alt="Operra"
            width={24}
            height={24}
            style={{ height: 24, width: 'auto', objectFit: 'contain' }}
          />
        </div>
        <ul className={styles.footerLinks}>
          <li><a href="#">Platform</a></li>
          <li><a href="#">Docs</a></li>
          <li><a href="#">Pricing</a></li>
          <li><a href="#">Blog</a></li>
          <li><a href="#">Careers</a></li>
          <li><a href="#">Status</a></li>
        </ul>
        <div className={styles.footerCopy}>© 2025 Operra. All rights reserved.</div>
      </div>
    </footer>
  )
}

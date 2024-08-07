from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField , PasswordField, SubmitField, BooleanField, SelectField, FileField, SelectMultipleField, widgets, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from src.models import Users, Instances, Hashes
from flask_wtf.file import FileAllowed, FileRequired

HASHCAT_ALGORITHMS = [
    ('', 'Auto detection'),
    ('-m 0', 'MD5'),
    ('-m 10', 'md5($pass.$salt) '),
    ('-m 20', 'md5($salt.$pass) '),
    ('-m 30', 'md5(utf16le($pass).$salt) '),
    ('-m 40', 'md5($salt.utf16le($pass)) '),
    ('-m 50', 'HMAC-MD5 (key = $pass) '),
    ('-m 60', 'HMAC-MD5 (key = $salt) '),
    ('-m 70', 'md5(utf16le($pass)) '),
    ('-m 100', 'SHA1 '),
    ('-m 110', 'sha1($pass.$salt) '),
    ('-m 120', 'sha1($salt.$pass) '),
    ('-m 130', 'sha1(utf16le($pass).$salt) '),
    ('-m 140', 'sha1($salt.utf16le($pass)) '),
    ('-m 150', 'HMAC-SHA1 (key = $pass) '),
    ('-m 160', 'HMAC-SHA1 (key = $salt) '),
    ('-m 170', 'sha1(utf16le($pass)) '),
    ('-m 200', 'MySQL323 '),
    ('-m 300', 'MySQL4.1/MySQL5 '),
    ('-m 400', 'phpass, WordPress (MD5), Joomla (MD5) '),
    ('-m 400', 'phpass, phpBB3 (MD5) '),
    ('-m 500', 'md5crypt, MD5 (Unix), Cisco-IOS $1$ (MD5) 2 '),
    ('-m 501', 'Juniper IVE '),
    ('-m 600', 'BLAKE2b-512 '),
    ('-m 610', 'BLAKE2b-512($pass.$salt) '),
    ('-m 620', 'BLAKE2b-512($salt.$pass) '),
    ('-m 900', 'MD4 '),
    ('-m 1000', 'NTLM '),
    ('-m 1100', 'Domain Cached Credentials (DCC), MS Cache '),
    ('-m 1300', 'SHA2-224 '),
    ('-m 1400', 'SHA2-256 '),
    ('-m 1410', 'sha256($pass.$salt) '),
    ('-m 1420', 'sha256($salt.$pass) '),
    ('-m 1430', 'sha256(utf16le($pass).$salt) '),
    ('-m 1440', 'sha256($salt.utf16le($pass)) '),
    ('-m 1450', 'HMAC-SHA256 (key = $pass) '),
    ('-m 1460', 'HMAC-SHA256 (key = $salt) '),
    ('-m 1470', 'sha256(utf16le($pass)) '),
    ('-m 1500', 'descrypt, DES (Unix), Traditional DES '),
    ('-m 1600', 'Apache $apr1$ MD5, md5apr1, MD5 (APR) 2 '),
    ('-m 1700', 'SHA2-512 '),
    ('-m 1710', 'sha512($pass.$salt) '),
    ('-m 1720', 'sha512($salt.$pass) '),
    ('-m 1730', 'sha512(utf16le($pass).$salt) '),
    ('-m 1740', 'sha512($salt.utf16le($pass)) '),
    ('-m 1750', 'HMAC-SHA512 (key = $pass) '),
    ('-m 1760', 'HMAC-SHA512 (key = $salt) '),
    ('-m 1770', 'sha512(utf16le($pass)) '),
    ('-m 1800', 'sha512crypt $6$, SHA512 (Unix) 2 '),
    ('-m 2000', 'STDOUT '),
    ('-m 2100', 'Domain Cached Credentials 2 (DCC2), MS Cache 2 '),
    ('-m 2400', 'Cisco-PIX MD5 '),
    ('-m 2410', 'Cisco-ASA MD5 '),
    ('-m 2500', 'WPA-EAPOL-PBKDF2 1 '),
    ('-m 2501', 'WPA-EAPOL-PMK 14 '),
    ('-m 2600', 'md5(md5($pass)) '),
    ('-m 2630', 'md5(md5($pass.$salt)) * '),
    ('-m 3000', 'LM '),
    ('-m 3100', 'Oracle H: Type (Oracle 7+) '),
    ('-m 3200', 'bcrypt $2*$, Blowfish (Unix) '),
    ('-m 3500', 'md5(md5(md5($pass))) '),
    ('-m 3610', 'md5(md5(md5($pass)).$salt) * '),
    ('-m 3710', 'md5($salt.md5($pass)) '),
    ('-m 3730', 'Dahua NVR/DVR/HVR (md5($salt1.strtoupper(md5($salt2.$pass)))) * '),
    ('-m 3800', 'md5($salt.$pass.$salt) '),
    ('-m 3910', 'md5(md5($pass).md5($salt)) '),
    ('-m 4010', 'md5($salt.md5($salt.$pass)) '),
    ('-m 4110', 'md5($salt.md5($pass.$salt)) '),
    ('-m 4300', 'md5(strtoupper(md5($pass))) '),
    ('-m 4400', 'md5(sha1($pass)) '),
    ('-m 4410', 'md5(sha1($pass).$salt) '),
    ('-m 4420', 'md5(sha1($pass.$salt)) * '),
    ('-m 4430', 'md5(sha1($salt.$pass)) * '),
    ('-m 4500', 'sha1(sha1($pass)) '),
    ('-m 4510', 'sha1(sha1($pass).$salt) '),
    ('-m 4520', 'sha1($salt.sha1($pass)) '),
    ('-m 4700', 'sha1(md5($pass)) '),
    ('-m 4710', 'sha1(md5($pass).$salt) '),
    ('-m 4800', 'iSCSI CHAP authentication, MD5(CHAP) 7 '),
    ('-m 4900', 'sha1($salt.$pass.$salt) '),
    ('-m 5000', 'sha1(sha1($salt.$pass.$salt)) '),
    ('-m 5100', 'Half MD5 '),
    ('-m 5200', 'Password Safe v3 '),
    ('-m 5300', 'IKE-PSK MD5 '),
    ('-m 5400', 'IKE-PSK SHA1 '),
    ('-m 5500', 'NetNTLMv1 / NetNTLMv1+ESS '),
    ('-m 5600', 'NetNTLMv2 '),
    ('-m 5700', 'Cisco-IOS type 4 (SHA256) '),
    ('-m 5800', 'Samsung Android Password/PIN '),
    ('-m 6000', 'RIPEMD-160 '),
    ('-m 6050', 'HMAC-RIPEMD160 (key = $pass) * '),
    ('-m 6060', 'HMAC-RIPEMD160 (key = $salt) * '),
    ('-m 6100', 'Whirlpool '),
    ('-m 6211', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES (legacy) '),
    ('-m 6211', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent (legacy) '),
    ('-m 6211', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Twofish (legacy) '),
    ('-m 6212', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES-Twofish (legacy) '),
    ('-m 6213', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES-Twofish-Serpent (legacy) '),
    ('-m 6212', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent-AES (legacy) '),
    ('-m 6213', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent-Twofish-AES (legacy) '),
    ('-m 6212', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Twofish-Serpent (legacy) '),
    ('-m 6221', 'TrueCrypt 5.0+ SHA512 + AES (legacy) '),
    ('-m 6221', 'TrueCrypt 5.0+ SHA512 + Serpent (legacy) '),
    ('-m 6221', 'TrueCrypt 5.0+ SHA512 + Twofish (legacy) '),
    ('-m 6222', 'TrueCrypt 5.0+ SHA512 + AES-Twofish (legacy) '),
    ('-m 6223', 'TrueCrypt 5.0+ SHA512 + AES-Twofish-Serpent (legacy) '),
    ('-m 6222', 'TrueCrypt 5.0+ SHA512 + Serpent-AES (legacy) '),
    ('-m 6223', 'TrueCrypt 5.0+ SHA512 + Serpent-Twofish-AES (legacy) '),
    ('-m 6222', 'TrueCrypt 5.0+ SHA512 + Twofish-Serpent (legacy) '),
    ('-m 6231', 'TrueCrypt 5.0+ Whirlpool + AES (legacy) '),
    ('-m 6231', 'TrueCrypt 5.0+ Whirlpool + Serpent (legacy) '),
    ('-m 6231', 'TrueCrypt 5.0+ Whirlpool + Twofish (legacy) '),
    ('-m 6232', 'TrueCrypt 5.0+ Whirlpool + AES-Twofish (legacy) '),
    ('-m 6233', 'TrueCrypt 5.0+ Whirlpool + AES-Twofish-Serpent (legacy) '),
    ('-m 6232', 'TrueCrypt 5.0+ Whirlpool + Serpent-AES (legacy) '),
    ('-m 6233', 'TrueCrypt 5.0+ Whirlpool + Serpent-Twofish-AES (legacy) '),
    ('-m 6232', 'TrueCrypt 5.0+ Whirlpool + Twofish-Serpent (legacy) '),
    ('-m 6241', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES + boot (legacy) '),
    ('-m 6241', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent + boot (legacy) '),
    ('-m 6241', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Twofish + boot (legacy) '),
    ('-m 6242', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES-Twofish + boot (legacy) '),
    ('-m 6243', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + AES-Twofish-Serpent + boot (legacy) '),
    ('-m 6242', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent-AES + boot (legacy) '),
    ('-m 6243', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Serpent-Twofish-AES + boot (legacy) '),
    ('-m 6242', 'TrueCrypt 5.0+ PBKDF2-HMAC-RIPEMD160 + Twofish-Serpent + boot (legacy) '),
    ('-m 6300', 'AIX {smd5} '),
    ('-m 6400', 'AIX {ssha256} '),
    ('-m 6500', 'AIX {ssha512} '),
    ('-m 6600', '1Password, agilekeychain '),
    ('-m 6700', 'AIX {ssha1} '),
    ('-m 6800', 'LastPass + LastPass sniffed4 '),
    ('-m 6900', 'GOST R 34.11-94 '),
    ('-m 7000', 'FortiGate (FortiOS) '),
    ('-m 7200', 'GRUB 2 '),
    ('-m 7300', 'IPMI2 RAKP HMAC-SHA1 '),
    ('-m 7350', 'IPMI2 RAKP HMAC-MD5 * '),
    ('-m 7400', 'sha256crypt $5$, SHA256 (Unix) 2 '),
    ('-m 7500', 'Kerberos 5, etype 23, AS-REQ Pre-Auth '),
    ('-m 7700', 'SAP CODVN B (BCODE) '),
    ('-m 7701', 'SAP CODVN B (BCODE) from RFC_READ_TABLE '),
    ('-m 7800', 'SAP CODVN F/G (PASSCODE) '),
    ('-m 7801', 'SAP CODVN F/G (PASSCODE) from RFC_READ_TABLE '),
    ('-m 7900', 'Drupal7 '),
    ('-m 8000', 'Sybase ASE '),
    ('-m 8100', 'Citrix NetScaler (SHA1) '),
    ('-m 8200', '1Password, cloudkeychain '),
    ('-m 8300', 'DNSSEC (NSEC3) '),
    ('-m 8400', 'WBB3 (Woltlab Burning Board) '),
    ('-m 8500', 'RACF '),
    ('-m 8600', 'Lotus Notes/Domino 5 '),
    ('-m 8700', 'Lotus Notes/Domino 6 '),
    ('-m 8800', 'Android FDE <= 4.3 '),
    ('-m 8900', 'scrypt '),
    ('-m 9000', 'Password Safe v2 '),
    ('-m 9100', 'Lotus Notes/Domino 8 '),
    ('-m 9200', 'Cisco-IOS $8$ (PBKDF2-SHA256) '),
    ('-m 9300', 'Cisco-IOS $9$ (scrypt) '),
    ('-m 9400', 'MS Office 2007 '),
    ('-m 9500', 'MS Office 2010 '),
    ('-m 9600', 'MS Office 2013 '),
    ('-m 9700', 'MS Office ⇐ 2003 MD5 + RC4, oldoffice$0, oldoffice$1 '),
    ('-m 9710', 'MS Office ⇐ 2003 $0/$1, MD5 + RC4, collider #1 23 '),
    ('-m 9720', 'MS Office ⇐ 2003 $0/$1, MD5 + RC4, collider #2 '),
    ('-m 9800', 'MS Office ⇐ 2003 SHA1 + RC4, oldoffice$3, oldoffice$4 '),
    ('-m 9810', 'MS Office ⇐ 2003 $3, SHA1 + RC4, collider #1 24 '),
    ('-m 9820', 'MS Office ⇐ 2003 $3, SHA1 + RC4, collider #2 '),
    ('-m 9900', 'Radmin2 '),
    ('-m 10000', 'Django (PBKDF2-SHA256) '),
    ('-m 10100', 'SipHash '),
    ('-m 10200', 'CRAM-MD5 '),
    ('-m 10300', 'SAP CODVN H (PWDSALTEDHASH) iSSHA-1 '),
    ('-m 10400', 'PDF 1.1 - 1.3 (Acrobat 2 - 4) '),
    ('-m 10410', 'PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #1 25 '),
    ('-m 10420', 'PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #2 '),
    ('-m 10500', 'PDF 1.4 - 1.6 (Acrobat 5 - 8) '),
    ('-m 10600', 'PDF 1.7 Level 3 (Acrobat 9) '),
    ('-m 10700', 'PDF 1.7 Level 8 (Acrobat 10 - 11) '),
    ('-m 10800', 'SHA2-384 '),
    ('-m 10810', 'sha384($pass.$salt) '),
    ('-m 10820', 'sha384($salt.$pass) '),
    ('-m 10830', 'sha384(utf16le($pass).$salt) '),
    ('-m 10840', 'sha384($salt.utf16le($pass)) '),
    ('-m 10870', 'sha384(utf16le($pass)) '),
    ('-m 10900', 'PBKDF2-HMAC-SHA256 '),
    ('-m 10901', 'RedHat 389-DS LDAP (PBKDF2-HMAC-SHA256) '),
    ('-m 11000', 'PrestaShop '),
    ('-m 11100', 'PostgreSQL CRAM (MD5) '),
    ('-m 11200', 'MySQL CRAM (SHA1) '),
    ('-m 11300', 'Bitcoin/Litecoin wallet.dat '),
    ('-m 11400', 'SIP digest authentication (MD5) '),
    ('-m 11500', 'CRC32 5 '),
    ('-m 11600', '7-Zip '),
    ('-m 11700', 'GOST R 34.11-2012 (Streebog) 256-bit, big-endian '),
    ('-m 11750', 'HMAC-Streebog-256 (key = $pass), big-endian '),
    ('-m 11760', 'HMAC-Streebog-256 (key = $salt), big-endian '),
    ('-m 11800', 'GOST R 34.11-2012 (Streebog) 512-bit, big-endian '),
    ('-m 11850', 'HMAC-Streebog-512 (key = $pass), big-endian '),
    ('-m 11860', 'HMAC-Streebog-512 (key = $salt), big-endian '),
    ('-m 11900', 'PBKDF2-HMAC-MD5 '),
    ('-m 12000', 'PBKDF2-HMAC-SHA1 '),
    ('-m 12100', 'PBKDF2-HMAC-SHA512 '),
    ('-m 12200', 'eCryptfs '),
    ('-m 12300', 'Oracle T: Type (Oracle 12+) '),
    ('-m 12400', 'BSDi Crypt, Extended DES '),
    ('-m 12500', 'RAR3-hp '),
    ('-m 12600', 'ColdFusion 10+ '),
    ('-m 12700', 'Blockchain, My Wallet '),
    ('-m 12800', 'MS-AzureSync PBKDF2-HMAC-SHA256 '),
    ('-m 12900', 'Android FDE (Samsung DEK) '),
    ('-m 13000', 'RAR5 '),
    ('-m 13100', 'Kerberos 5, etype 23, TGS-REP '),
    ('-m 13200', 'AxCrypt 1 '),
    ('-m 13300', 'AxCrypt 1 in-memory SHA1 13 '),
    ('-m 13400', 'KeePass 1 AES / without keyfile '),
    ('-m 13400', 'KeePass 2 AES / without keyfile '),
    ('-m 13400', 'KeePass 1 Twofish / with keyfile '),
    ('-m 13400', 'Keepass 2 AES / with keyfile '),
    ('-m 13500', 'PeopleSoft PS_TOKEN '),
    ('-m 13600', 'WinZip '),
    ('-m 13711', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + AES (legacy) '),
    ('-m 13712', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + AES-Twofish (legacy) '),
    ('-m 13711', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + Serpent (legacy) '),
    ('-m 13712', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + Serpent-AES (legacy) '),
    ('-m 13713', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + Serpent-Twofish-AES (legacy) '),
    ('-m 13711', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + Twofish (legacy) '),
    ('-m 13712', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + Twofish-Serpent (legacy) '),
    ('-m 13751', 'VeraCrypt PBKDF2-HMAC-SHA256 + AES (legacy) '),
    ('-m 13752', 'VeraCrypt PBKDF2-HMAC-SHA256 + AES-Twofish (legacy) '),
    ('-m 13751', 'VeraCrypt PBKDF2-HMAC-SHA256 + Serpent (legacy) '),
    ('-m 13752', 'VeraCrypt PBKDF2-HMAC-SHA256 + Serpent-AES (legacy) '),
    ('-m 13753', 'VeraCrypt PBKDF2-HMAC-SHA256 + Serpent-Twofish-AES (legacy) '),
    ('-m 13751', 'VeraCrypt PBKDF2-HMAC-SHA256 + Twofish (legacy) '),
    ('-m 13752', 'VeraCrypt PBKDF2-HMAC-SHA256 + Twofish-Serpent (legacy) '),
    ('-m 13721', 'VeraCrypt PBKDF2-HMAC-SHA512 + AES (legacy) '),
    ('-m 13722', 'VeraCrypt PBKDF2-HMAC-SHA512 + AES-Twofish (legacy) '),
    ('-m 13721', 'VeraCrypt PBKDF2-HMAC-SHA512 + Serpent (legacy) '),
    ('-m 13722', 'VeraCrypt PBKDF2-HMAC-SHA512 + Serpent-AES (legacy) '),
    ('-m 13723', 'VeraCrypt PBKDF2-HMAC-SHA512 + Serpent-Twofish-AES (legacy) '),
    ('-m 13721', 'VeraCrypt PBKDF2-HMAC-SHA512 + Twofish (legacy) '),
    ('-m 13722', 'VeraCrypt PBKDF2-HMAC-SHA512 + Twofish-Serpent (legacy) '),
    ('-m 13731', 'VeraCrypt PBKDF2-HMAC-Whirlpool + AES (legacy) '),
    ('-m 13732', 'VeraCrypt PBKDF2-HMAC-Whirlpool + AES-Twofish (legacy) '),
    ('-m 13731', 'VeraCrypt PBKDF2-HMAC-Whirlpool + Serpent (legacy) '),
    ('-m 13732', 'VeraCrypt PBKDF2-HMAC-Whirlpool + Serpent-AES (legacy) '),
    ('-m 13733', 'VeraCrypt PBKDF2-HMAC-Whirlpool + Serpent-Twofish-AES (legacy) '),
    ('-m 13731', 'VeraCrypt PBKDF2-HMAC-Whirlpool + Twofish (legacy) '),
    ('-m 13732', 'VeraCrypt PBKDF2-HMAC-Whirlpool + Twofish-Serpent (legacy) '),
    ('-m 13741', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + boot-mode + AES (legacy) '),
    ('-m 13742', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + boot-mode + AES-Twofish (legacy) '),
    ('-m 13743', 'VeraCrypt PBKDF2-HMAC-RIPEMD160 + boot-mode + AES-Twofish-Serpent (legacy) '),
    ('-m 13761', 'VeraCrypt PBKDF2-HMAC-SHA256 + boot-mode + Twofish (legacy) '),
    ('-m 13762', 'VeraCrypt PBKDF2-HMAC-SHA256 + boot-mode + Serpent-AES (legacy) '),
    ('-m 13763', 'VeraCrypt PBKDF2-HMAC-SHA256 + boot-mode + Serpent-Twofish-AES (legacy) '),
    ('-m 13761', 'VeraCrypt PBKDF2-HMAC-SHA256 + boot-mode + PIM + AES 16 (legacy) '),
    ('-m 13771', 'VeraCrypt Streebog-512 + XTS 512 bit (legacy) '),
    ('-m 13772', 'VeraCrypt Streebog-512 + XTS 1024 bit (legacy) '),
    ('-m 13773', 'VeraCrypt Streebog-512 + XTS 1536 bit (legacy) '),
    ('-m 13781', 'VeraCrypt Streebog-512 + XTS 512 bit + boot-mode (legacy) '),
    ('-m 13782', 'VeraCrypt Streebog-512 + XTS 1024 bit + boot-mode (legacy) '),
    ('-m 13783', 'VeraCrypt Streebog-512 + XTS 1536 bit + boot-mode (legacy) '),
    ('-m 13800', 'Windows Phone 8+ PIN/password '),
    ('-m 13900', 'OpenCart '),
    ('-m 14000', 'DES (PT = $salt, key = $pass) 8 '),
    ('-m 14100', '3DES (PT = $salt, key = $pass) 9 '),
    ('-m 14400', 'sha1(CX) '),
    ('-m 14500', 'Linux Kernel Crypto API (2.4) '),
    ('-m 14600', 'LUKS v1 (legacy) 10 '),
    ('-m 14700', 'iTunes backup < 10.0 11 '),
    ('-m 14800', 'iTunes backup >= 10.0 11 '),
    ('-m 14900', 'Skip32 (PT = $salt, key = $pass) 12 '),
    ('-m 15000', 'FileZilla Server >= 0.9.55 '),
    ('-m 15100', 'Juniper/NetBSD sha1crypt '),
    ('-m 15200', 'Blockchain, My Wallet, V2 '),
    ('-m 15300', 'DPAPI masterkey file v1 + local context '),
    ('-m 15310', 'DPAPI masterkey file v1 (context 3) * '),
    ('-m 15400', 'ChaCha20 20 '),
    ('-m 15500', 'JKS Java Key Store Private Keys (SHA1) '),
    ('-m 15600', 'Ethereum Wallet, PBKDF2-HMAC-SHA256 '),
    ('-m 15700', 'Ethereum Wallet, SCRYPT '),
    ('-m 15900', 'DPAPI masterkey file v2 + Active Directory domain context '),
    ('-m 15910', 'DPAPI masterkey file v2 (context 3) '),
    ('-m 16000', 'Tripcode '),
    ('-m 16100', 'TACACS+ '),
    ('-m 16200', 'Apple Secure Notes '),
    ('-m 16300', 'Ethereum Pre-Sale Wallet, PBKDF2-HMAC-SHA256 '),
    ('-m 16400', 'CRAM-MD5 Dovecot '),
    ('-m 16500', 'JWT (JSON Web Token) '),
    ('-m 16600', 'Electrum Wallet (Salt-Type 1-3) '),
    ('-m 16700', 'FileVault 2 '),
    ('-m 16800', 'WPA-PMKID-PBKDF2 1 '),
    ('-m 16801', 'WPA-PMKID-PMK 15 '),
    ('-m 16900', 'Ansible Vault '),
    ('-m 17010', 'GPG (AES-128/AES-256 (SHA-1($pass))) * '),
    ('-m 17020', 'GPG (AES-128/AES-256 (SHA-512($pass))) * '),
    ('-m 17030', 'GPG (AES-128/AES-256 (SHA-256($pass))) * '),
    ('-m 17200', 'PKZIP (Compressed) '),
    ('-m 17210', 'PKZIP (Uncompressed) '),
    ('-m 17220', 'PKZIP (Compressed Multi-File) '),
    ('-m 17225', 'PKZIP (Mixed Multi-File) '),
    ('-m 17230', 'PKZIP (Mixed Multi-File Checksum-Only) '),
    ('-m 17300', 'SHA3-224 '),
    ('-m 17400', 'SHA3-256 '),
    ('-m 17500', 'SHA3-384 '),
    ('-m 17600', 'SHA3-512 '),
    ('-m 17700', 'Keccak-224 '),
    ('-m 17800', 'Keccak-256 '),
    ('-m 17900', 'Keccak-384 '),
    ('-m 18000', 'Keccak-512 '),
    ('-m 18100', 'TOTP (HMAC-SHA1) '),
    ('-m 18200', 'Kerberos 5, etype 23, AS-REP '),
    ('-m 18300', 'Apple File System (APFS) '),
    ('-m 18400', 'Open Document Format (ODF) 1.2 (SHA-256, AES) '),
    ('-m 18500', 'sha1(md5(md5($pass))) '),
    ('-m 18600', 'Open Document Format (ODF) 1.1 (SHA-1, Blowfish) '),
    ('-m 18700', 'Java Object hashCode() '),
    ('-m 18800', 'Blockchain, My Wallet, Second Password (SHA256) '),
    ('-m 18900', 'Android Backup '),
    ('-m 19000', 'QNX /etc/shadow (MD5) '),
    ('-m 19100', 'QNX /etc/shadow (SHA256) '),
    ('-m 19200', 'QNX /etc/shadow (SHA512) '),
    ('-m 19300', 'sha1($salt1.$pass.$salt2) '),
    ('-m 19500', 'Ruby on Rails Restful-Authentication '),
    ('-m 19600', 'Kerberos 5, etype 17, TGS-REP (AES128-CTS-HMAC-SHA1-96) '),
    ('-m 19700', 'Kerberos 5, etype 18, TGS-REP (AES256-CTS-HMAC-SHA1-96) '),
    ('-m 19800', 'Kerberos 5, etype 17, Pre-Auth '),
    ('-m 19900', 'Kerberos 5, etype 18, Pre-Auth '),
    ('-m 20011', 'DiskCryptor SHA512 + XTS 512 bit (AES) '),
    ('-m 20011', 'DiskCryptor SHA512 + XTS 512 bit (Twofish) '),
    ('-m 20011', 'DiskCryptor SHA512 + XTS 512 bit (Serpent) '),
    ('-m 20012', 'DiskCryptor SHA512 + XTS 1024 bit (AES-Twofish) '),
    ('-m 20012', 'DiskCryptor SHA512 + XTS 1024 bit (Twofish-Serpent) '),
    ('-m 20012', 'DiskCryptor SHA512 + XTS 1024 bit (Serpent-AES) '),
    ('-m 20013', 'DiskCryptor SHA512 + XTS 1536 bit (AES-Twofish-Serpent) '),
    ('-m 20200', 'Python passlib pbkdf2-sha512 '),
    ('-m 20300', 'Python passlib pbkdf2-sha256 '),
    ('-m 20400', 'Python passlib pbkdf2-sha1 '),
    ('-m 20500', 'PKZIP Master Key '),
    ('-m 20510', 'PKZIP Master Key (6 byte optimization) 17 '),
    ('-m 20600', 'Oracle Transportation Management (SHA256) '),
    ('-m 20710', 'sha256(sha256($pass).$salt) '),
    ('-m 20712', 'RSA Security Analytics / NetWitness (sha256) * '),
    ('-m 20720', 'sha256($salt.sha256($pass)) '),
    ('-m 20800', 'sha256(md5($pass)) '),
    ('-m 20900', 'md5(sha1($pass).md5($pass).sha1($pass)) '),
    ('-m 21000', 'BitShares v0.x - sha512(sha512_bin(pass)) '),
    ('-m 21100', 'sha1(md5($pass.$salt)) '),
    ('-m 21200', 'md5(sha1($salt).md5($pass)) '),
    ('-m 21300', 'md5($salt.sha1($salt.$pass)) '),
    ('-m 21310', 'md5($salt1.sha1($salt2.$pass)) * '),
    ('-m 21400', 'sha256(sha256_bin($pass)) '),
    ('-m 21420', 'sha256($salt.sha256_bin($pass)) '),
    ('-m 21500', 'SolarWinds Orion '),
    ('-m 21501', 'SolarWinds Orion v2 '),
    ('-m 21600', 'Web2py pbkdf2-sha512 '),
    ('-m 21700', 'Electrum Wallet (Salt-Type 4) '),
    ('-m 21800', 'Electrum Wallet (Salt-Type 5) '),
    ('-m 22000', 'WPA-PBKDF2-PMKID+EAPOL 1 '),
    ('-m 22000', 'WPA-PBKDF2-PMKID+EAPOL 1 '),
    ('-m 22001', 'WPA-PMK-PMKID+EAPOL 18 '),
    ('-m 22100', 'BitLocker '),
    ('-m 22200', 'Citrix NetScaler (SHA512) '),
    ('-m 22300', 'sha256($salt.$pass.$salt) '),
    ('-m 22400', 'AES Crypt (SHA256) '),
    ('-m 22500', 'MultiBit Classic .key (MD5) '),
    ('-m 22600', 'Telegram Desktop < v2.1.14 (PBKDF2-HMAC-SHA1) '),
    ('-m 22700', 'MultiBit HD (scrypt) '),
    ('-m 22911', 'RSA/DSA/EC/OpenSSH Private Keys ($0$)'),
    ('-m 22921', 'RSA/DSA/EC/OpenSSH Private Keys ($6$)'),
    ('-m 22931', 'RSA/DSA/EC/OpenSSH Private Keys ($1, $3$)'),
    ('-m 22941', 'RSA/DSA/EC/OpenSSH Private Keys ($4$)'),
    ('-m 22951', 'RSA/DSA/EC/OpenSSH Private Keys ($5$)'),
    ('-m 23001', 'SecureZIP AES-128 '),
    ('-m 23002', 'SecureZIP AES-192 '),
    ('-m 23003', 'SecureZIP AES-256 '),
    ('-m 23100', 'Apple Keychain '),
    ('-m 23200', 'XMPP SCRAM PBKDF2-SHA1 '),
    ('-m 23300', 'Apple iWork'),
    ('-m 23400', 'Bitwarden '),
    ('-m 23500', 'AxCrypt 2 AES-128'),
    ('-m 23600', 'AxCrypt 2 AES-256'),
    ('-m 23700', 'RAR3-p (Uncompressed)'),
    ('-m 23800', 'RAR3-p (Compressed)'),
    ('-m 23900', 'BestCrypt v3 Volume Encryption'),
    ('-m 24100', 'MongoDB ServerKey SCRAM-SHA-1 '),
    ('-m 24200', 'MongoDB ServerKey SCRAM-SHA-256 '),
    ('-m 24300', 'sha1($salt.sha1($pass.$salt)) '),
    ('-m 24410', 'PKCS#8 Private Keys (PBKDF2-HMAC-SHA1 + 3DES/AES)'),
    ('-m 24420', 'PKCS#8 Private Keys (PBKDF2-HMAC-SHA256 + 3DES/AES)'),
    ('-m 24500', 'Telegram Desktop >= v2.1.14 (PBKDF2-HMAC-SHA512) '),
    ('-m 24600', 'SQLCipher'),
    ('-m 24700', 'Stuffit5 '),
    ('-m 24800', 'Umbraco HMAC-SHA1 '),
    ('-m 24900', 'Dahua Authentication MD5 '),
    ('-m 25000', 'SNMPv3 HMAC-MD5-96/HMAC-SHA1-96 8 '),
    ('-m 25100', 'SNMPv3 HMAC-MD5-96 8 '),
    ('-m 25200', 'SNMPv3 HMAC-SHA1-96 8 '),
    ('-m 25300', 'MS Office 2016 - SheetProtection '),
    ('-m 25400', 'PDF 1.4 - 1.6 (Acrobat 5 - 8) - user and owner pass '),
    ('-m 25500', 'Stargazer Stellar Wallet XLM '),
    ('-m 25600', 'bcrypt(md5($pass)) / bcryptmd5 '),
    ('-m 25700', 'MurmurHash '),
    ('-m 25800', 'bcrypt(sha1($pass)) / bcryptsha1 '),
    ('-m 25900', 'KNX IP Secure - Device Authentication Code '),
    ('-m 26000', 'Mozilla key3.db '),
    ('-m 26100', 'Mozilla key4.db '),
    ('-m 26200', 'OpenEdge Progress Encode '),
    ('-m 26300', 'FortiGate256 (FortiOS256) '),
    ('-m 26401', 'AES-128-ECB NOKDF (PT = $salt, key = $pass) '),
    ('-m 26402', 'AES-192-ECB NOKDF (PT = $salt, key = $pass) '),
    ('-m 26403', 'AES-256-ECB NOKDF (PT = $salt, key = $pass) '),
    ('-m 26500', 'iPhone passcode (UID key + System Keybag) '),
    ('-m 26600', 'MetaMask Wallet 8 '),
    ('-m 26610', 'MetaMask Wallet (short hash, plaintext check) 8 * '),
    ('-m 26700', 'SNMPv3 HMAC-SHA224-128 8 '),
    ('-m 26800', 'SNMPv3 HMAC-SHA256-192 8 8 '),
    ('-m 26900', 'SNMPv3 HMAC-SHA384-256 8 '),
    ('-m 27000', 'NetNTLMv1 / NetNTLMv1+ESS (NT) 22 '),
    ('-m 27100', 'NetNTLMv2 (NT) 22 '),
    ('-m 27200', 'Ruby on Rails Restful Auth (one round, no sitekey) '),
    ('-m 27300', 'SNMPv3 HMAC-SHA512-384 8 '),
    ('-m 27400', 'VMware VMX (PBKDF2-HMAC-SHA1 + AES-256-CBC) '),
    ('-m 27500', 'VirtualBox (PBKDF2-HMAC-SHA256 & AES-128-XTS) '),
    ('-m 27600', 'VirtualBox (PBKDF2-HMAC-SHA256 & AES-256-XTS) '),
    ('-m 27700', 'MultiBit Classic .wallet (scrypt) '),
    ('-m 27800', 'MurmurHash3 '),
    ('-m 27900', 'CRC32C '),
    ('-m 28000', 'CRC64Jones '),
    ('-m 28100', 'Windows Hello PIN/Password '),
    ('-m 28200', 'Exodus Desktop Wallet (scrypt) '),
    ('-m 28300', 'Teamspeak 3 (channel hash) '),
    ('-m 28400', 'bcrypt(sha512($pass)) / bcryptsha512 '),
    ('-m 28501', 'Bitcoin WIF private key (P2PKH), compressed 26 '),
    ('-m 28502', 'Bitcoin WIF private key (P2PKH), uncompressed 27'),
    ('-m 28503', 'Bitcoin WIF private key (P2WPKH, Bech32), compressed 28 '),
    ('-m 28504', 'Bitcoin WIF private key (P2WPKH, Bech32), uncompressed 29 '),
    ('-m 28505', 'Bitcoin WIF private key (P2SH(P2WPKH)), compressed 30 '),
    ('-m 28506', 'Bitcoin WIF private key (P2SH(P2WPKH)), uncompressed 31 '),
    ('-m 28600', 'PostgreSQL SCRAM-SHA-256 '),
    ('-m 28700', 'Amazon AWS4-HMAC-SHA256 '),
    ('-m 28800', 'Kerberos 5, etype 17, DB '),
    ('-m 28900', 'Kerberos 5, etype 18, DB '),
    ('-m 29000', 'sha1($salt.sha1(utf16le($username).:.utf16le($pass))) '),
    ('-m 29100', 'Flask Session Cookie ($salt.$salt.$pass) '),
    ('-m 29200', 'Radmin3 '),
    ('-m 29311', 'TrueCrypt RIPEMD160 + XTS 512 bit '),
    ('-m 29312', 'TrueCrypt RIPEMD160 + XTS 1024 bit '),
    ('-m 29313', 'TrueCrypt RIPEMD160 + XTS 1536 bit '),
    ('-m 29321', 'TrueCrypt SHA512 + XTS 512 bit '),
    ('-m 29322', 'TrueCrypt SHA512 + XTS 1024 bit '),
    ('-m 29323', 'TrueCrypt SHA512 + XTS 1536 bit '),
    ('-m 29331', 'TrueCrypt Whirlpool + XTS 512 bit '),
    ('-m 29332', 'TrueCrypt Whirlpool + XTS 1024 bit '),
    ('-m 29333', 'TrueCrypt Whirlpool + XTS 1536 bit '),
    ('-m 29341', 'TrueCrypt RIPEMD160 + XTS 512 bit + boot-mode '),
    ('-m 29342', 'TrueCrypt RIPEMD160 + XTS 1024 bit + boot-mode '),
    ('-m 29343', 'TrueCrypt RIPEMD160 + XTS 1536 bit + boot-mode '),
    ('-m 29411', 'VeraCrypt RIPEMD160 + XTS 512 bit '),
    ('-m 29412', 'VeraCrypt RIPEMD160 + XTS 1024 bit '),
    ('-m 29413', 'VeraCrypt RIPEMD160 + XTS 1536 bit '),
    ('-m 29421', 'VeraCrypt SHA512 + XTS 512 bit '),
    ('-m 29422', 'VeraCrypt SHA512 + XTS 1024 bit '),
    ('-m 29423', 'VeraCrypt SHA512 + XTS 1536 bit '),
    ('-m 29431', 'VeraCrypt Whirlpool + XTS 512 bit '),
    ('-m 29432', 'VeraCrypt Whirlpool + XTS 1024 bit '),
    ('-m 29433', 'VeraCrypt Whirlpool + XTS 1536 bit '),
    ('-m 29441', 'VeraCrypt RIPEMD160 + XTS 512 bit + boot-mode '),
    ('-m 29442', 'VeraCrypt RIPEMD160 + XTS 1024 bit + boot-mode '),
    ('-m 29443', 'VeraCrypt RIPEMD160 + XTS 1536 bit + boot-mode '),
    ('-m 29451', 'VeraCrypt SHA256 + XTS 512 bit '),
    ('-m 29452', 'VeraCrypt SHA256 + XTS 1024 bit '),
    ('-m 29453', 'VeraCrypt SHA256 + XTS 1536 bit '),
    ('-m 29461', 'VeraCrypt SHA256 + XTS 512 bit + boot-mode '),
    ('-m 29462', 'VeraCrypt SHA256 + XTS 1024 bit + boot-mode '),
    ('-m 29463', 'VeraCrypt SHA256 + XTS 1536 bit + boot-mode '),
    ('-m 29471', 'VeraCrypt Streebog-512 + XTS 512 bit '),
    ('-m 29472', 'VeraCrypt Streebog-512 + XTS 1024 bit '),
    ('-m 29473', 'VeraCrypt Streebog-512 + XTS 1536 bit '),
    ('-m 29481', 'VeraCrypt Streebog-512 + XTS 512 bit + boot-mode '),
    ('-m 29482', 'VeraCrypt Streebog-512 + XTS 1024 bit + boot-mode '),
    ('-m 29483', 'VeraCrypt Streebog-512 + XTS 1536 bit + boot-mode '),
    ('-m 29511', 'LUKS v1 SHA-1 + AES '),
    ('-m 29512', 'LUKS v1 SHA-1 + Serpent '),
    ('-m 29513', 'LUKS v1 SHA-1 + Twofish '),
    ('-m 29521', 'LUKS v1 SHA-256 + AES '),
    ('-m 29522', 'LUKS v1 SHA-256 + Serpent '),
    ('-m 29523', 'LUKS v1 SHA-256 + Twofish '),
    ('-m 29531', 'LUKS v1 SHA-512 + AES '),
    ('-m 29532', 'LUKS v1 SHA-512 + Serpent '),
    ('-m 29533', 'LUKS v1 SHA-512 + Twofish '),
    ('-m 29541', 'LUKS v1 RIPEMD-160 + AES '),
    ('-m 29542', 'LUKS v1 RIPEMD-160 + Serpent '),
    ('-m 29543', 'LUKS v1 RIPEMD-160 + Twofish '),
    ('-m 29700', 'KeePass 1 (AES/Twofish) and KeePass 2 (AES) - keyfile only mode 32 '),
    ('-m 29800', 'Bisq .wallet (scrypt) * '),
    ('-m 29910', 'ENCsecurity Datavault (PBKDF2/no keychain) * '),
    ('-m 29920', 'ENCsecurity Datavault (PBKDF2/keychain) * '),
    ('-m 29930', 'ENCsecurity Datavault (MD5/no keychain) * '),
    ('-m 29940', 'ENCsecurity Datavault (MD5/keychain) * '),
    ('-m 30000', 'Python Werkzeug MD5 (HMAC-MD5 (key = $salt)) * '),
    ('-m 30120', 'Python Werkzeug SHA256 (HMAC-SHA256 (key = $salt)) * '),
    ('-m 30420', 'DANE RFC7929/RFC8162 SHA2-256 * '),
    ('-m 30500', 'md5(md5($salt).md5(md5($pass))) * '),
    ('-m 30600', 'bcrypt(sha256($pass)) / bcryptsha256 * '),
    ('-m 30700', 'Anope IRC Services (enc_sha256) * '),
    ('-m 30901', 'Bitcoin raw private key (P2PKH), compressed 33 * '),
    ('-m 30902', 'Bitcoin raw private key (P2PKH), uncompressed 34 * '),
    ('-m 30903', 'Bitcoin raw private key (P2WPKH, Bech32), compressed 35 * '),
    ('-m 30904', 'Bitcoin raw private key (P2WPKH, Bech32), uncompressed 36 * '),
    ('-m 30905', 'Bitcoin raw private key (P2SH(P2WPKH)), compressed 37 * '),
    ('-m 30906', 'Bitcoin raw private key (P2SH(P2WPKH)), uncompressed 38 * '),
    ('-m 31000', 'BLAKE2s-256 * '),
    ('-m 31100', 'SM3 * '),
    ('-m 31200', 'Veeam VBK * '),
    ('-m 31300', 'MS SNTP * '),
    ('-m 99999',	'Plaintext *' )
]

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already in use. Please choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
def file_size_limit(max_size):
    max_bytes = max_size * 1024 * 1024
    def _file_size_limit(form, field):
        if field.data:
            if len(field.data.read()) > max_bytes:
                raise ValidationError(f'File size must be less than {max_size} MB')
            field.data.seek(0)  # reset file pointer to beginning after reading
    return _file_size_limit

class CrackStationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=60)], render_kw={'placeholder': 'MyHash'})
    hash = FileField('Hash File (Max size: 200MB)', validators=[DataRequired(), FileAllowed(['txt'], 'TXT files only!')])
    wordlist = MultiCheckboxField(
        'Wordlist',
        choices=[
            ('rockyou', 'rockyou'), 
            ('common-passwords-win', 'common-passwords-win'), 
            ('10k-most-common', '10k-most-common'),
            ('active-directory-wordlists', 'active-directory-wordlists'),
            ('richelieu-top1000', 'richelieu-top1000')
        ],
        validators=[Optional()]  # Use Optional because actual requirement is checked in a custom validator
    )
    use_custom_wordlist = BooleanField('Use Custom Wordlist')
    custom_wordlist = FileField('Custom Wordlist', validators=[FileAllowed(['txt'], 'TXT files only!'), Optional()])
    algorithm = SelectField(
        'Algorithm',
        choices=HASHCAT_ALGORITHMS,
        
    )
    provider = SelectField(
        'Provider',
        choices=[('', 'Choice ...'), ('AWS', 'AWS')],
        validators=[DataRequired()],
    )
    power = SelectField(
        'Instance Performance',
        choices=[('', 'Choice ...'), ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        validators=[DataRequired()],
    )
    price_limit = DecimalField('Price Limit', validators=[Optional(), NumberRange(min=5, max=1000000, message='Price limit must be between 10 and 1 000 000')], render_kw={'placeholder': 'Enter price limit', 'step': '0.01'})
    submit = SubmitField('Crack It!')

    def validate_wordlist(self, field):
        if not field.data and not (self.use_custom_wordlist.data and self.custom_wordlist.data and self.custom_wordlist.data.filename):
            raise ValidationError('Please select at least one wordlist or upload a custom wordlist.')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already in use. Please choose another one.')
            
class AdminUpdateAccountForm(FlaskForm):
    user_id=StringField('User ID')
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField(
        'Role',
        choices=[('', 'Change role'), ('user', 'User'), ('admin', 'Admin')]
    )
    submit = SubmitField('Saves Changes')

    def validate_username(self, username):
        user = Users.query.get(self.user_id.data)
        if user and username.data != user.username:
            user_with_same_username = Users.query.filter_by(username=username.data).first()
            if user_with_same_username:
                raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        user = Users.query.get(self.user_id.data)
        if user and email.data != user.email:
            user_with_same_email = Users.query.filter_by(email=email.data).first()
            if user_with_same_email:
                raise ValidationError('This email is already in use. Please choose another one.')
            

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
        
class ResumeHashForm(FlaskForm):
    hash_id=StringField('Hash ID')
    provider = SelectField(
        'Provider',
        choices=[('', 'Choice ...'), ('AWS', 'AWS')],
        validators=[DataRequired()]
    )
    power = SelectField(
        'Power',
        choices=[('', 'Change power'), ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],validators=[DataRequired()]
    )
    price_limit = DecimalField('Price Limit', validators=[Optional(), NumberRange(min=5, max=1000000, message='Price limit must be between 10 and 1 000 000')], render_kw={'placeholder': 'Enter price limit', 'step': '0.01'})
    submit = SubmitField('Crack again !')
import { defineConfig } from '@prisma/config'
import * as dotenv from 'dotenv'

dotenv.config()

export default defineConfig({
  schema: './prisma/schema.prisma',
  earlyAccess: true,
  datasource: {
    url: process.env.NEON_DATABASE_URL
  }
})

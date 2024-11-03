// supabaseClient.js
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config();
const supabaseUrl = process.env.POSTGRES_URL;
const supabaseKey = process.env.SUPABASE_API_KEY;
console.log(supabaseUrl)
export const supabase = createClient(supabaseUrl, supabaseKey);

import { supabase } from "./supabaseClient";

export const updateSupabaseUser = async (clerkUserId: string, email: string) => {
  try {
    const { data, error: findError } = await supabase
      .from('public_user_info')
      .select('user_id')
      .eq('user_id', clerkUserId)
      .maybeSingle();

    if (findError) throw findError;

    if (!data) {
      const { error: insertError } = await supabase
        .from('public_user_info')
        .insert([{ user_id: clerkUserId, email: email }]); // Include the email in the insert

      if (insertError) throw insertError;
    }
  } catch (error) {
    console.error('Error updating Supabase user:', error);
  }
};
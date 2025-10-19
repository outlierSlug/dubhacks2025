export type RatingInputs = {
  utr?: number;
  skillLevel: number; // 1-3
  yearsPlayed: number;
  hasCompExperience: boolean;
};

export class TennisRating {
  private static readonly MAX_YEARS = 14;
  private static readonly UTR_MAX = 16.5;
  private static readonly SKILL_MULTIPLIER = 5;
  private static readonly SKILL_ADDER = 3;
  private static readonly EXPERIENCE_MULTIPLIER = 2;
  private static readonly COMPETITION_BONUS = 10;
  
  /**
   * Calculates a tennis player's rating on a scale of 0-100
   * @param inputs Player statistics and experience
   * @returns Rating between 0-100
   */
  public static calculate(inputs: RatingInputs): number {
    const baseScore = this.calculateBaseScore(inputs.skillLevel);
    const experienceBonus = this.calculateExperienceBonus(inputs.yearsPlayed);
    const competitionBonus = this.calculateCompetitionBonus(inputs.hasCompExperience);
    const compositeScore = baseScore + experienceBonus + competitionBonus;

    if (inputs.utr === undefined) {
      return Math.min(compositeScore, 70);
    }

    return this.calculateWithUTR(inputs.utr, compositeScore);
  }

  private static calculateBaseScore(skillLevel: number): number {
    return (skillLevel * this.SKILL_MULTIPLIER) + this.SKILL_ADDER;
  }

  private static calculateExperienceBonus(years: number): number {
    return Math.min(years, this.MAX_YEARS) * this.EXPERIENCE_MULTIPLIER;
  }

  private static calculateCompetitionBonus(hasCompetitive: boolean): number {
    return hasCompetitive ? this.COMPETITION_BONUS : 0;
  }

  private static calculateWithUTR(utr: number, compositeScore: number): number {
    const utrScore = (utr / this.UTR_MAX) * 100;

    if (utr >= 10) {
      return Math.min(utrScore, 100);
    }

    const weights = this.getWeights(utr);
    const rating = (utrScore * weights.utr) + (compositeScore * weights.composite);
    
    return Math.min(rating, 95);
  }

  private static getWeights(utr: number): { utr: number; composite: number } {
    if (utr >= 4) {
      return { utr: 0.5, composite: 0.5 };
    }
    return { utr: 0.2, composite: 0.8 };
  }
}